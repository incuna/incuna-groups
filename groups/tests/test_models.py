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
    def test_for_group_pk(self):
        discussion = factories.DiscussionFactory.create()
        comment = factories.CommentFactory.create(discussion=discussion)
        factories.CommentFactory.create()

        results = models.Comment.objects.for_discussion_pk(discussion.pk)
        self.assertCountEqual([comment], results)


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

            # From Comment
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


class TestComment(Python2AssertMixin, TestCase):
    def test_fields(self):
        fields = models.Comment._meta.get_all_field_names()
        expected = wipe_id_fields_on_django_lt_17([
            'id',
            'body',
            'discussion',
            'discussion_id',
            'user',
            'user_id',
            'date_created',
        ])
        self.assertCountEqual(fields, expected)

    def test_get_absolute_url(self):
        comment = factories.CommentFactory.create()
        expected = '/groups/discussions/{}/'.format(comment.discussion.pk)
        self.assertEqual(comment.get_absolute_url(), expected)
