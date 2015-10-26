from django.test import TestCase
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .. import models


class TestGroup(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.Group._meta.get_all_field_names()
        expected = {
            'id',
            'name',
            'is_private',
            'moderators',
            'watchers',
            'members_if_private',

            # From Discussion
            'discussions',
        }
        self.assertCountEqual(fields, expected)

    def test_get_absolute_url(self):
        group = factories.GroupFactory.create()
        expected = '/groups/{}/'.format(group.pk)
        self.assertEqual(group.get_absolute_url(), expected)


class TestDiscussion(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.Discussion._meta.get_all_field_names()
        expected = [
            'id',
            'name',
            'group',
            'group_id',
            'creator',
            'creator_id',
            'date_created',
            'subscribers',
            'ignorers',

            # From BaseComment
            'comments',
        ]
        self.assertCountEqual(fields, expected)

    def test_get_absolute_url(self):
        discussion = factories.DiscussionFactory.create()
        expected = '/groups/discussions/{}/'.format(discussion.pk)
        self.assertEqual(discussion.get_absolute_url(), expected)

    def test_ordering(self):
        discussion_one, discussion_two = factories.DiscussionFactory.create_batch(2)

        discussions = models.Discussion.objects.all()
        expected = [discussion_two, discussion_one]
        self.assertSequenceEqual(discussions, expected)


class TestBaseComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.BaseComment._meta.get_all_field_names()
        expected = [
            'id',
            'discussion',
            'discussion_id',
            'user',
            'user_id',
            'date_created',
            'state',

            'polymorphic_ctype',
            'polymorphic_ctype_id',
            'textcomment',
            'filecomment',
        ]
        self.assertCountEqual(fields, expected)

    def test_get_pagejump_anchor(self):
        comment = factories.TextCommentFactory.create()
        expected = 'c{}'.format(comment.pk)
        self.assertEqual(comment.get_pagejump_anchor(), expected)

    def test_get_pagejump(self):
        comment = factories.TextCommentFactory.create()
        expected = '#c{}'.format(comment.pk)
        self.assertEqual(comment.get_pagejump(), expected)

    def test_get_absolute_url(self):
        comment = factories.TextCommentFactory.create()
        expected = '/groups/discussions/{}/#c{}'.format(comment.discussion.pk, comment.pk)
        self.assertEqual(comment.get_absolute_url(), expected)

    def test_may_be_deleted_comment_user(self):
        comment = factories.TextCommentFactory.create()
        self.assertTrue(comment.may_be_deleted(comment.user))

    def test_may_be_deleted_admin(self):
        comment = factories.TextCommentFactory.create()
        admin = factories.AdminFactory.create()
        self.assertTrue(comment.may_be_deleted(admin))

    def test_may_be_deleted_other_user(self):
        comment = factories.TextCommentFactory.create()
        user = factories.UserFactory.create()
        self.assertFalse(comment.may_be_deleted(user))

    def test_may_be_deleted_already_deleted(self):
        comment = factories.TextCommentFactory.create()
        comment.delete_state()
        self.assertFalse(comment.may_be_deleted(comment.user))

    def test_delete_state(self):
        comment = factories.TextCommentFactory.create()
        self.assertEqual(comment.state, comment.STATE_OK)
        comment.delete_state()
        self.assertEqual(comment.state, comment.STATE_DELETED)

    def test_is_deleted(self):
        comment = factories.TextCommentFactory.create()
        self.assertFalse(comment.is_deleted())
        comment.delete_state()
        self.assertTrue(comment.is_deleted())


class TestBaseCommentSubscribers(Python2AssertMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comment = factories.BaseCommentFactory.create()
        cls.subscriber, cls.other = factories.UserFactory.create_batch(2)

    def test_subscribers_discussion(self):
        """The users subscribed to the discussion are included."""
        self.comment.discussion.subscribers.add(self.subscriber)

        subscribers = self.comment.subscribers()

        self.assertIn(self.subscriber, subscribers)
        self.assertNotIn(self.other, subscribers)

    def test_subscribers_group(self):
        """The users watching the group are included."""
        self.comment.discussion.group.watchers.add(self.subscriber)

        subscribers = self.comment.subscribers()

        self.assertIn(self.subscriber, subscribers)
        self.assertNotIn(self.other, subscribers)

    def test_subscribers_comment_poster(self):
        """The comment poster is not included even if subscribed."""
        self.comment.discussion.subscribers.add(self.comment.user)
        self.comment.discussion.group.watchers.add(self.comment.user)

        subscribers = self.comment.subscribers()

        self.assertNotIn(self.comment.user, subscribers)

    def test_subscribers_ignored_discussion(self):
        """A group watcher is excluded if they ignore the discussion."""
        self.comment.discussion.ignorers.add(self.other)
        self.comment.discussion.group.watchers.add(self.other)

        subscribers = self.comment.subscribers()

        self.assertNotIn(self.other, subscribers)

    def test_subscribers_duplicate(self):
        """A subscriber to discussion and group is not counted twice."""
        self.comment.discussion.subscribers.add(self.subscriber)
        self.comment.discussion.group.watchers.add(self.subscriber)

        subscribers = self.comment.subscribers()

        self.assertCountEqual([self.subscriber], subscribers)


class TestTextComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.TextComment._meta.get_all_field_names()
        expected = [
            'id',
            'body',
            'discussion',
            'discussion_id',
            'user',
            'user_id',
            'date_created',
            'state',

            'polymorphic_ctype',
            'polymorphic_ctype_id',
            'basecomment_ptr',
            'basecomment_ptr_id',
        ]
        self.assertCountEqual(fields, expected)


class TestFileComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.FileComment._meta.get_all_field_names()
        expected = [
            'id',
            'file',
            'discussion',
            'discussion_id',
            'user',
            'user_id',
            'date_created',
            'state',

            'polymorphic_ctype',
            'polymorphic_ctype_id',
            'basecomment_ptr',
            'basecomment_ptr_id',
        ]
        self.assertCountEqual(fields, expected)
