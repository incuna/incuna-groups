from django.core.urlresolvers import reverse

from . import factories
from .utils import RenderedContentTestCase
from ..views import discussions, groups


class TestGroupList(RenderedContentTestCase):
    view = groups.GroupList

    def test_list_display(self):
        group = factories.GroupFactory.create()
        expected_content = {
            group.name: True,
            reverse('group-detail', kwargs={'pk': group.pk}): True,
        }

        self.render_view_and_assert_content(expected_content)


class TestGroupDetail(RenderedContentTestCase):
    view = groups.GroupDetail

    def test_detail_display(self):
        group = factories.GroupFactory.create()
        discussion = factories.DiscussionFactory.create(group=group)
        expected_content = {
            group.name: True,
            discussion.name: True,
            reverse('discussion-thread', kwargs={'pk': discussion.pk}): True,
        }

        self.render_view_and_assert_content(expected_content, pk=group.pk)


class TestDiscussionThread(RenderedContentTestCase):
    view = discussions.DiscussionThread

    def test_text_comment_display(self):
        comment_body = 'I am a comment and proud of it!'
        comment = factories.TextCommentFactory.create(
            body=comment_body,
        )
        discussion = comment.discussion

        expected_content = {
            discussion.name: True,
            comment_body: True,
            str(comment.user): True,
            reverse('discussion-subscribe', kwargs={'pk': discussion.pk}): True,
            'Post comment': True,  # The label on the 'add comment' button
            'type="submit"': True,  # The button itself
        }

        self.render_view_and_assert_content(expected_content, pk=discussion.pk)

    def test_file_comment_display(self):
        comment = factories.FileCommentFactory.create()
        discussion = comment.discussion

        expected_content = {
            discussion.name: True,
            comment.file.url: True,
            comment.file.name: True,
            str(comment.user): True,
            reverse('discussion-subscribe', kwargs={'pk': discussion.pk}): True,
            'Post comment': True,  # The label on the 'add comment' button
            'type="submit"': True,  # The button itself
        }

        self.render_view_and_assert_content(expected_content, pk=discussion.pk)
