from django.core import signing
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

    def test_str(self):
        group = factories.GroupFactory.create()
        self.assertEqual(str(group), group.name)

    def test_get_all_comments(self):
        """Assert this method returns all comments on the group and no more."""
        group = factories.GroupFactory.create()
        comments = factories.BaseCommentFactory.create_batch(2, discussion__group=group)
        factories.BaseCommentFactory.create()  # unrelated comment

        self.assertSequenceEqual(list(group.get_all_comments()), comments)

    def test_get_latest_comment(self):
        """Assert that this method returns the most recent comment on the group."""
        group = factories.GroupFactory.create()
        factories.BaseCommentFactory.create(discussion__group=group)
        latest_on_group = factories.BaseCommentFactory.create(discussion__group=group)
        factories.BaseCommentFactory.create()  # unrelated comment

        self.assertEqual(group.get_latest_comment(), latest_on_group)

    def test_get_total_commenters(self):
        """Assert that this method returns the number of unique posters on the group."""
        group = factories.GroupFactory.create()
        comments = factories.BaseCommentFactory.create_batch(2, discussion__group=group)
        factories.BaseCommentFactory.create(
            discussion__group=group,
            user=comments[0].user,
        )

        self.assertEqual(group.get_total_commenters(), 2)

    def test_get_total_discussions(self):
        """Assert that this method returns the number of discussions on the group."""
        group = factories.GroupFactory.create()
        factories.DiscussionFactory.create(group=group)
        factories.DiscussionFactory.create()  # unrelated discussion
        self.assertEqual(group.get_total_discussions(), 1)


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

    def test_str(self):
        discussion = factories.DiscussionFactory.create()
        self.assertEqual(str(discussion), discussion.name)

    def test_generate_reply_uuid(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        expected_data = {
            'discussion_pk': discussion.pk,
            'user_pk': user.pk,
        }

        signed_data = discussion.generate_reply_uuid(user)
        self.assertEqual(signing.loads(signed_data), expected_data)


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

    def test_str(self):
        comment = factories.TextCommentFactory.create()
        self.assertEqual(
            str(comment),
            '{} on Discussion #{}'.format(
                'TextComment',
                comment.discussion_id
            )
        )


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

    def test_short_filename(self):
        filename = '/groups/file_comments/name.txt'
        comment = factories.FileCommentFactory.create(file__filename=filename)
        self.assertEqual(comment.short_filename(), 'name.txt')
