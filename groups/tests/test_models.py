import datetime

from django.core import signing
from django.test import TestCase
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .. import models


class TestGroup(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = [f.name for f in models.Group._meta.get_fields()]
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
        fields = [f.name for f in models.Discussion._meta.get_fields()]
        expected = [
            'id',
            'name',
            'group',
            'creator',
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

    def test_get_latest_comment(self):
        """This method returns the most recent comment."""
        discussion = factories.DiscussionFactory.create()
        latest = factories.BaseCommentFactory.create(discussion=discussion)
        factories.BaseCommentFactory.create(
            discussion=discussion,
            date_created=datetime.datetime(1970, 1, 1),
        )

        self.assertEqual(discussion.get_latest_comment(), latest)


class TestBaseComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = [f.name for f in models.BaseComment._meta.get_fields()]
        expected = [
            'id',
            'discussion',
            'user',
            'date_created',
            'state',
            'attachments',

            'polymorphic_ctype',
            'textcomment',
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
        fields = [f.name for f in models.TextComment._meta.get_fields()]
        expected = [
            'id',
            'body',
            'discussion',
            'user',
            'date_created',
            'state',
            'attachments',

            'polymorphic_ctype',
            'basecomment_ptr',
        ]
        self.assertCountEqual(fields, expected)


class TestAttachedFile(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = [f.name for f in models.AttachedFile._meta.get_fields()]
        expected = [
            'id',
            'file',
            'user',
            'date_created',
            'attached_to',
        ]
        self.assertCountEqual(fields, expected)

    def test_short_filename(self):
        filename = '/groups/file_comments/test_attached_file_comment.txt'
        comment = factories.AttachedFileFactory.create(file__filename=filename)
        self.assertEqual(comment.short_filename(), 'test_attached_file_comment.txt')
