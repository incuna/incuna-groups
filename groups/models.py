from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


class DiscussionManager(models.Manager):
    def for_group_pk(self, pk):
        return self.get_queryset().filter(group_id=pk)


class CommentManager(models.Manager):
    def for_discussion_pk(self, pk):
        return self.get_queryset().filter(discussion_id=pk)


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


class Comment(models.Model):
    """A model for a comment in a discussion thread."""
    body = models.TextField()
    discussion = models.ForeignKey('groups.Discussion', related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    date_created = models.DateTimeField(default=timezone.now)

    objects = CommentManager()

    class Meta:
        ordering = ('date_created',)

    def get_absolute_url(self):
        return reverse('discussion-thread', kwargs={'pk': self.discussion.pk})
