import datetime

from django.test import TestCase
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .. import models


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

    def test_active(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        results = models.Group.objects.active()
        self.assertCountEqual([comment.discussion.group], results)

    def test_active_distinct(self):
        group = factories.GroupFactory.create()
        factories.TextCommentFactory.create_batch(
            2,
            date_created=datetime.date.today(),
            discussion__group=group,
        )

        self.assertCountEqual([group], models.Group.objects.active())


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

    def test_active(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        results = models.Discussion.objects.active()
        self.assertCountEqual([comment.discussion], results)

    def test_active_distinct(self):
        discussion = factories.DiscussionFactory.create()
        factories.TextCommentFactory.create_batch(
            2,
            date_created=datetime.date.today(),
            discussion=discussion,
        )

        self.assertCountEqual([discussion], models.Discussion.objects.active())


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

    def test_recent(self):
        comment = factories.TextCommentFactory.create(date_created=datetime.date.today())
        factories.TextCommentFactory.create(date_created=datetime.date(1970, 1, 1))

        self.assertCountEqual([comment], models.BaseComment.objects.recent())

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
