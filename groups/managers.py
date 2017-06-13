import datetime

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet


DEFAULT_WITHIN_DAYS = apps.get_app_config('groups').default_within_days


class WithinDaysQuerySetMixin:
    """
    A mixin that adds methods for returning items that have recently been posted (to).

    Can be mixed into a Manager or a QuerySet.

    Requires a `since_filter` member on the inheriting class, which is the condition used
    by the since() method. To set up the mixin for use in a `User` manager or queryset,
    use:

        since_filter = 'comments__date_created__gte'
    """
    @staticmethod
    def get_threshold_delta(timedelta):
        """Return the earliest posting *time* an item can have and still be recent."""
        return datetime.datetime.now() - timedelta

    @staticmethod
    def get_threshold_date(within_days=DEFAULT_WITHIN_DAYS):
        """Return the earliest posting *date* an item can have and still be recent."""
        return datetime.date.today() - datetime.timedelta(days=within_days)

    def within_days(self, days=DEFAULT_WITHIN_DAYS):
        """All users that created an item within the last `days` days."""
        return self.since(self.get_threshold_date(days))

    def within_time(self, timedelta):
        """All users that created an item within the last `timedelta`."""
        return self.since(self.get_threshold_delta(timedelta))

    def since(self, when):
        """All the comments belonging to items in this queryset posted since `when`."""
        since_filter = {self.since_filter: when}
        return self.filter(**since_filter).distinct()


class GroupQuerySet(WithinDaysQuerySetMixin, models.QuerySet):
    """A queryset for Groups allowing for smarter retrieval of related objects."""
    since_filter = 'discussions__comments__date_created__gte'

    def discussions(self):
        """All the discussions on these groups."""
        from .models import Discussion
        return Discussion.objects.filter(group__in=self)

    def comments(self):
        """All the comments posted in these groups."""
        from .models import BaseComment
        return BaseComment.objects.filter(discussion__group__in=self)

    def users(self):
        """All the users who have ever posted in these groups."""
        User = get_user_model()
        return User.objects.filter(comments__in=self.comments()).distinct()


class DiscussionQuerySet(WithinDaysQuerySetMixin, models.QuerySet):
    """A queryset for Discussions allowing for smarter retrieval of related objects."""
    since_filter = 'comments__date_created__gte'

    def for_group(self, group):
        """All the discussions on a particular group."""
        return self.filter(group=group)

    def comments(self):
        """All the comments on these discussions."""
        from .models import BaseComment
        return BaseComment.objects.filter(discussion__in=self)

    def users(self):
        """All the users who have ever posted in these discussions."""
        User = get_user_model()
        return User.objects.filter(comments__discussion__in=self).distinct()

    def with_last_updated(self):
        return self.annotate(last_updated=models.Max('comments__date_created'))


class CommentManagerMixin(WithinDaysQuerySetMixin):
    """
    Provides methods suitable for use on both a queryset and a manager for BaseComments.

    django-polymorphic's managers/querysets don't play well with related managers, so we
    have to force its hand a bit.

    Based on https://djangosnippets.org/snippets/2114/.
    """
    since_filter = 'date_created__gte'

    def for_group(self, group):
        """All the comments on a particular group."""
        return self.filter(discussion__group=group)

    def for_discussion(self, discussion):
        """All the comments on a particular discussion."""
        return self.filter(discussion=discussion)

    def users(self):
        """All the users who, between them, posted these comments."""
        User = get_user_model()
        return User.objects.filter(comments__in=self.all()).distinct()

    def with_user_may_delete(self, user):
        """
        Return a list of comments annotated with 'user_may_delete' values.

        The value denotes if the passed-in user is allowed to delete this particular
        comment. The method returns a list instead of a QuerySet to avoid removing the
        added variable with further filters.
        """
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
