from django.contrib.auth import get_user_model
from django.db import models
from polymorphic import PolymorphicManager, PolymorphicQuerySet


class GroupQuerySet(models.QuerySet):
    """A queryset for Groups allowing for smarter retrieval of related objects."""
    def discussions(self):
        """All the discussions on these groups."""
        from .models import Discussion
        return Discussion.objects.filter(group__in=self).distinct()

    def comments(self):
        """All the comments posted in these groups."""
        from .models import BaseComment
        return BaseComment.objects.filter(discussion__group__in=self).distinct()

    def users(self):
        """All the users who have ever posted in these groups."""
        User = get_user_model()
        return User.objects.filter(comments__in=self.comments()).distinct()


class DiscussionQuerySet(models.QuerySet):
    """A queryset for Discussions allowing for smarter retrieval of related objects."""
    def for_group_pk(self, pk):
        """All the discussions on a particular group."""
        return self.filter(group_id=pk)

    def comments(self):
        """All the comments on these discussions."""
        from .models import BaseComment
        return BaseComment.objects.filter(discussion__in=self).distinct()

    def users(self):
        """All the users who have ever posted in these discussions."""
        User = get_user_model()
        return User.objects.filter(comments__discussion__in=self).distinct()


class CommentManagerMixin:
    """
    Provides methods suitable for use on both a queryset and a manager for BaseComments.

    django-polymorphic's managers/querysets don't play well with related managers, so we
    have to force its hand a bit.

    Based on https://djangosnippets.org/snippets/2114/.
    """
    def for_group_pk(self, pk):
        """All the comments on a particular group."""
        return self.filter(discussion__group_id=pk)

    def for_discussion_pk(self, pk):
        """All the comments on a particular discussion."""
        return self.filter(discussion_id=pk)

    def users(self):
        """All the users who, between them, posted these comments."""
        User = get_user_model()
        return User.objects.filter(comments__in=self.all()).distinct()

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
