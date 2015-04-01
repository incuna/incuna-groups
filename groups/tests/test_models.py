from django.test import TestCase
from incuna_test_utils.compat import (
    Python2AssertMixin,
    wipe_id_fields_on_django_lt_17
)

from . import factories
from .. import models


class TestDiscussionManager(Python2AssertMixin, TestCase):
    def test_for_group_pk(self):
        group = factories.GroupFactory.create()
        discussion = factories.DiscussionFactory.create(group=group)
        factories.DiscussionFactory.create()

        results = models.Discussion.objects.for_group_pk(group.pk)
        self.assertCountEqual([discussion], results)


class TestCommentManager(Python2AssertMixin, TestCase):
    def test_for_discussion_pk(self):
        discussion = factories.DiscussionFactory.create()
        comment = factories.TextCommentFactory.create(discussion=discussion)
        factories.TextCommentFactory.create()

        results = models.BaseComment.objects.for_discussion_pk(discussion.pk)
        self.assertCountEqual([comment], results)

    def test_with_user_may_delete(self):
        comment_one = factories.TextCommentFactory.create()
        comment_two = factories.TextCommentFactory.create()

        results = models.BaseComment.objects.with_user_may_delete(comment_one.user)
        self.assertCountEqual([comment_one, comment_two], results)

        may_delete_values = [comment.user_may_delete for comment in results]
        self.assertCountEqual([True, False], may_delete_values)


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
        expected = wipe_id_fields_on_django_lt_17([
            'id',
            'name',
            'group',
            'group_id',
            'creator',
            'creator_id',
            'date_created',
            'subscribers',

            # From BaseComment
            'comments',
        ])
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
        expected = wipe_id_fields_on_django_lt_17([
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
        ])
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


class TestTextComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.TextComment._meta.get_all_field_names()
        expected = wipe_id_fields_on_django_lt_17([
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
        ])
        self.assertCountEqual(fields, expected)


class TestFileComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.FileComment._meta.get_all_field_names()
        expected = wipe_id_fields_on_django_lt_17([
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
        ])
        self.assertCountEqual(fields, expected)
