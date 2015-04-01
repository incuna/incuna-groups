from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from polymorphic import PolymorphicManager, PolymorphicModel


class DiscussionManager(models.Manager):
    def for_group_pk(self, pk):
        return self.filter(group_id=pk)


class CommentManager(PolymorphicManager):
    def for_discussion_pk(self, pk):
        return self.filter(discussion_id=pk)

    def with_user_may_delete(self, user):
        """Return a list to avoid removing the added variable with further filters."""
        comments = list(self.all())
        for comment in comments:
            comment.user_may_delete = comment.may_be_deleted(user)

        return comments


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

    objects = DiscussionManager()

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
    body = models.TextField()

    class Meta(BaseComment.Meta):
        pass


class FileComment(BaseComment):
    file = models.FileField()

    class Meta(BaseComment.Meta):
        pass
