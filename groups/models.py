from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.template import loader, RequestContext
from django.utils import timezone
from polymorphic import PolymorphicManager, PolymorphicModel, PolymorphicQuerySet


class GroupQuerySet(models.QuerySet):
    """A queryset for Groups allowing for smarter retrieval of related objects."""
    def discussions(self):
        return Discussion.objects.filter(group__in=self)

    def comments(self):
        return BaseComment.objects.filter(discussion__group__in=self)

    def users(self):
        User = get_user_model()
        return User.objects.filter(comments__in=self.comments())


class DiscussionQuerySet(models.QuerySet):
    """A queryset for Discussions allowing for smarter retrieval of related objects."""
    def for_group_pk(self, pk):
        return self.filter(group_id=pk)

    def comments(self):
        return BaseComment.objects.filter(discussion__in=self)

    def users(self):
        User = get_user_model()
        return User.objects.filter(comments__discussion__in=self)


class CommentManagerMixin:
    """
    Provides methods suitable for use on both a queryset and a manager for BaseComments.

    django-polymorphic's managers/querysets don't play well with related managers, so we
    have to force its hand a bit.

    Based on https://djangosnippets.org/snippets/2114/.
    """
    def for_group_pk(self, pk):
        return self.filter(discussion__group_id=pk)

    def for_discussion_pk(self, pk):
        return self.filter(discussion_id=pk)

    def users(self):
        User = get_user_model()
        return User.objects.filter(comments__in=self.all())

    def with_user_may_delete(self, user):
        """Return a list to avoid removing the added variable with further filters."""
        comments = list(self.all())
        for comment in comments:
            comment.user_may_delete = comment.may_be_deleted(user)

        return comments


class CommentQuerySet(PolymorphicQuerySet, CommentManagerMixin):
    """A queryset for BaseComments allowing for smarter retrieval of related objects."""


class CommentManager(PolymorphicManager, CommentManagerMixin):
    """PolymorphicManager for BaseComments with custom methods."""
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)


class Group(models.Model):
    """
    A model for a discussion group, similar to a forum.

    Groups can be private, in which case users have to request to join before
    they can read and/or watch the group.  The 'members' field stores such
    users, and isn't used by non-private groups.
    """
    name = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='moderated_groups',
    )
    watchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='watched_groups',
    )
    members_if_private = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='private_groups_joined',
    )

    objects = GroupQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('group-detail', kwargs={'pk': self.pk})


class Discussion(models.Model):
    """A model for a discussion thread in a group."""
    name = models.CharField(max_length=255)
    group = models.ForeignKey('groups.Group', related_name='discussions')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_discussions',
    )
    date_created = models.DateTimeField(default=timezone.now)
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='subscribed_discussions',
    )

    objects = DiscussionQuerySet.as_manager()

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse('discussion-thread', kwargs={'pk': self.pk})

    def get_latest_comment(self):
        return self.comments.latest('date_created')

    def get_total_replies(self):
        return self.comments.count()


class BaseComment(PolymorphicModel):
    """A model for a comment in a discussion thread."""
    STATE_OK = 'ok'
    STATE_DELETED = 'deleted'
    STATE_CHOICES = (
        (STATE_OK, 'OK'),
        (STATE_DELETED, 'Deleted'),
    )

    discussion = models.ForeignKey('groups.Discussion', related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    date_created = models.DateTimeField(default=timezone.now)
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default=STATE_OK)

    objects = CommentManager()

    class Meta:
        ordering = ('date_created',)

    def get_pagejump_anchor(self):
        """Return a string suitable for use in a page jump to this comment."""
        return 'c{}'.format(self.pk)

    def get_pagejump(self):
        """Return the URL suffix that'll jump to this comment's anchor point."""
        return '#' + self.get_pagejump_anchor()

    def get_absolute_url(self):
        """Return a permalink that'll scroll to this comment on the page."""
        url = reverse('discussion-thread', kwargs={'pk': self.discussion.pk})
        return url + self.get_pagejump()

    def may_be_deleted(self, user):
        """Return true if the user is allowed to delete this comment, false otherwise."""
        if self.is_deleted():
            return False

        if user.is_superuser or user.is_staff:
            return True

        if user.pk == self.user.pk:
            return True

        return False

    def get_context_data(self):
        """Get the context data, used by `comment.render()`."""
        return {'comment': self}

    def render(self, request):
        """
        Render the comment in the template, used by `groups_tags.comment_render`.

        Enables simple override of the comment template, also simplifying the
        structure of `templates/groups/disucssion_thread_base.html`.
        """
        template = loader.get_template(self.template_name)
        context = RequestContext(request, self.get_context_data())
        return template.render(context)

    def delete_state(self):
        """
        Cause this comment to show as deleted.

        Named so as not to conflict with the model's built-in delete() method, which
        removes it from the database.
        """
        self.state = self.STATE_DELETED
        self.save()

    def is_deleted(self):
        return self.state == self.STATE_DELETED


class TextComment(BaseComment):
    """A normal comment consisting only of some text."""
    body = models.TextField()
    template_name = 'groups/text_comment.html'


class FileComment(BaseComment):
    """A comment with an uploaded file. No text."""
    file = models.FileField(upload_to='groups/file_comments')
    template_name = 'groups/file_comment.html'
