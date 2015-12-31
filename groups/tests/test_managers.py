import datetime

from django.contrib.auth.models import User
from django.db import models as django_models
from django.test import TestCase
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .. import managers, models


class TestGroupManager(Python2AssertMixin, TestCase):
    def test_discussions(self):
        discussion = factories.DiscussionFactory.create()
        discussion_two = factories.DiscussionFactory.create()

        results = models.Group.objects.discussions()
        self.assertCountEqual([discussion, discussion_two], results)

    def test_comments(self):
        comment = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()

        results = models.Group.objects.comments()
        self.assertCountEqual([comment, comment_two], results)

    def test_users(self):
        comment = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()
        factories.UserFactory.create()

        results = models.Group.objects.users()
        self.assertCountEqual([comment.user, comment_two.user], results)

    def test_users_distinct(self):
        """Assert that Group.objects.users() contains no duplicates."""
        user = factories.UserFactory.create()
        factories.TextCommentFactory.create_batch(2, user=user)

        self.assertCountEqual([user], models.Group.objects.users())

    def test_within_days(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        results = models.Group.objects.within_days()
        self.assertCountEqual([comment.discussion.group], results)

    def test_within_time(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        delta = datetime.timedelta(hours=6)

        results = models.Group.objects.within_time(delta)
        self.assertCountEqual([comment.discussion.group], results)

    def test_since(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        when = datetime.date(2000, 1, 1)

        results = models.Group.objects.since(when)
        self.assertCountEqual([comment.discussion.group], results)

    def test_within_days_distinct(self):
        """Assert that Group.objects.within_days() contains no duplicates."""
        group = factories.GroupFactory.create()
        factories.TextCommentFactory.create_batch(
            2,
            date_created=datetime.date.today(),
            discussion__group=group,
        )

        self.assertCountEqual([group], models.Group.objects.within_days())

    def test_within_time_distinct(self):
        """Assert that Group.objects.within_time() contains no duplicates."""
        group = factories.GroupFactory.create()
        factories.TextCommentFactory.create_batch(2, discussion__group=group)
        delta = datetime.timedelta(hours=6)

        self.assertCountEqual([group], models.Group.objects.within_time(delta))


class TestDiscussionManager(Python2AssertMixin, TestCase):
    def test_for_group(self):
        group = factories.GroupFactory.create()
        discussion = factories.DiscussionFactory.create(group=group)
        factories.DiscussionFactory.create()

        results = models.Discussion.objects.for_group(group)
        self.assertCountEqual([discussion], results)

    def test_comments(self):
        comment = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()

        results = models.Discussion.objects.comments()
        self.assertCountEqual([comment, comment_two], results)

    def test_users(self):
        comment = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()
        factories.UserFactory.create()

        results = models.Discussion.objects.users()
        self.assertCountEqual([comment.user, comment_two.user], results)

    def test_users_distinct(self):
        """Assert that Discussion.objects.users() contains no duplicates."""
        user = factories.UserFactory.create()
        factories.TextCommentFactory.create_batch(2, user=user)

        self.assertCountEqual([user], models.Discussion.objects.users())

    def test_chaining(self):
        """Assert that chaining some of the above methods together works properly."""
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create()
        group = comment.discussion.group

        results = models.Discussion.objects.for_group(group).comments()
        self.assertCountEqual([comment], results)

    def test_within_days(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        results = models.Discussion.objects.within_days()
        self.assertCountEqual([comment.discussion], results)

    def test_within_time(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        delta = datetime.timedelta(hours=6)

        results = models.Discussion.objects.within_time(delta)
        self.assertCountEqual([comment.discussion], results)

    def test_since(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        when = datetime.date(2000, 1, 1)

        results = models.Discussion.objects.since(when)
        self.assertCountEqual([comment.discussion], results)

    def test_within_days_distinct(self):
        """Assert that Discussion.objects.within_days() contains no duplicates."""
        discussion = factories.DiscussionFactory.create()
        factories.TextCommentFactory.create_batch(
            2,
            date_created=datetime.date.today(),
            discussion=discussion,
        )

        self.assertCountEqual([discussion], models.Discussion.objects.within_days())

    def test_within_time_distinct(self):
        """Assert that Discussion.objects.within_time() contains no duplicates."""
        discussion = factories.DiscussionFactory.create()
        factories.TextCommentFactory.create_batch(2, discussion=discussion)
        delta = datetime.timedelta(hours=6)

        self.assertCountEqual([discussion], models.Discussion.objects.within_time(delta))

    def test_with_last_updated(self):
        discussion = factories.DiscussionFactory.create()
        latest = factories.TextCommentFactory.create(
            discussion=discussion,
            date_created=datetime.datetime(2970, 1, 1)
        )
        factories.TextCommentFactory.create(
            discussion=discussion,
            date_created=datetime.datetime(1970, 1, 1)
        )

        last_updated = models.Discussion.objects.with_last_updated()
        self.assertEqual(last_updated.get().last_updated, latest.date_created)


class TestCommentManager(Python2AssertMixin, TestCase):
    def test_for_group(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create()

        results = models.BaseComment.objects.for_group(comment.discussion.group)
        self.assertCountEqual([comment], results)

    def test_for_discussion(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create()

        results = models.BaseComment.objects.for_discussion(comment.discussion)
        self.assertCountEqual([comment], results)

    def test_users(self):
        user = factories.TextCommentFactory.create().user
        user_two = factories.TextCommentFactory.create().user
        factories.UserFactory.create()

        results = models.BaseComment.objects.users()
        self.assertCountEqual([user, user_two], results)

    def test_users_distinct(self):
        """Assert that BaseComment.objects.users() contains no duplicates."""
        user = factories.UserFactory.create()
        factories.TextCommentFactory.create_batch(2, user=user)

        self.assertCountEqual([user], models.BaseComment.objects.users())

    def test_within_days(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        self.assertCountEqual([comment], models.BaseComment.objects.within_days())

    def test_within_time(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        delta = datetime.timedelta(hours=6)

        self.assertCountEqual([comment], models.BaseComment.objects.within_time(delta))

    def test_since(self):
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))
        when = datetime.date(2000, 1, 1)

        results = models.BaseComment.objects.since(when)
        self.assertCountEqual([comment], results)

    def test_chaining(self):
        """Assert that chaining some of the above methods together works properly."""
        comment = factories.TextCommentFactory.create()
        factories.TextCommentFactory.create()
        group = comment.discussion.group

        results = models.BaseComment.objects.for_group(group).users()
        self.assertCountEqual([comment.user], results)

    def test_with_user_may_delete(self):
        comment_one = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()

        results = models.BaseComment.objects.with_user_may_delete(comment_one.user)
        self.assertCountEqual([comment_one, comment_two], results)

        may_delete_values = [comment.user_may_delete for comment in results]
        self.assertCountEqual([True, False], may_delete_values)


class TestWithinDaysQuerySetMixin(Python2AssertMixin, TestCase):
    mixin = managers.WithinDaysQuerySetMixin

    def __init__(self, *args, **kwargs):
        """
        Declare some classes that will be used in this test.

        We need a manager and a queryset that inherit from the mixin
        being tested.

        We also set the model attribute on a manager instance to emulate
        adding the manager to a User model.
        """
        super(TestWithinDaysQuerySetMixin, self).__init__(*args, **kwargs)

        class MixedInQuerySet(self.mixin, django_models.QuerySet):
            """A basic QuerySet extending the mixin."""
            since_filter = 'comments__date_created__gte'

        class MixedInManager(self.mixin, django_models.Manager):
            """A basic Manager extending the mixin and using MixedInQuerySet."""
            since_filter = 'comments__date_created__gte'

            def get_queryset(self):
                return MixedInQuerySet(self.model, using=self._db)

        self.manager = MixedInManager()
        self.manager.model = User

    def setUp(self):
        self.recent_user = factories.UserFactory.create()
        factories.TextCommentFactory.create(user=self.recent_user)
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

    def test_within_days_in_manager(self):
        """Assert that within_days() works properly when called from the manager."""
        results = self.manager.within_days()
        self.assertCountEqual([self.recent_user], results)

    def test_within_days_in_queryset(self):
        """Assert that within_days() works properly when called from the queryset."""
        results = self.manager.all().within_days()
        self.assertCountEqual([self.recent_user], results)

    def test_within_time_in_manager(self):
        """Assert that within_time() works properly when called from the manager."""
        results = self.manager.within_time(datetime.timedelta(hours=6))
        self.assertCountEqual([self.recent_user], results)

    def test_within_time_in_queryset(self):
        """Assert that within_time() works properly when called from the queryset."""
        results = self.manager.all().within_time(datetime.timedelta(hours=6))
        self.assertCountEqual([self.recent_user], results)

    def test_since_in_manager(self):
        """Assert that since() works properly when called from the manager."""
        results = self.manager.since(datetime.date(2000, 1, 1))
        self.assertCountEqual([self.recent_user], results)

    def test_since_in_queryset(self):
        """Assert that since() works properly when called from the queryset."""
        results = self.manager.all().since(datetime.date(2000, 1, 1))
        self.assertCountEqual([self.recent_user], results)
