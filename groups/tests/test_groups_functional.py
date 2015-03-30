from django.core.urlresolvers import reverse

from groups import views
from groups.tests import factories

from .utils import RenderedContentTestCase


class TestGroupList(RenderedContentTestCase):
    view = views.GroupList

    def test_list_display(self):
        group = factories.GroupFactory.create()
        expected_content = {
            group.name: True,
            reverse('group-detail', kwargs={'pk': group.pk}): True,
        }

        self.render_view_and_assert_content(expected_content)


class TestGroupDetail(RenderedContentTestCase):
    view = views.GroupDetail

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
    view = views.DiscussionThread

    def test_discussion_display(self):
        comment_body = 'I am a comment and proud of it!'
        discussion = factories.DiscussionFactory.create()
        comment = factories.CommentFactory.create(
            body=comment_body,
            discussion=discussion
        )
        expected_content = {
            discussion.name: True,
            comment_body: True,
            str(comment.user): True,
            reverse('discussion-subscribe', kwargs={'pk': discussion.pk}): True,
            'Post comment': True,  # The label on the 'add comment' button
            'type="submit"': True,  # The button itself
        }

        self.render_view_and_assert_content(expected_content, pk=discussion.pk)
