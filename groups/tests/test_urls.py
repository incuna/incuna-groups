from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestGroupUrls(URLTestCase):
    pk = 42

    def test_group_list(self):
        self.assert_url_matches_view(
            views.groups.GroupList,
            '/groups/',
            'group-list',
        )

    def test_group_detail(self):
        self.assert_url_matches_view(
            views.groups.GroupDetail,
            '/groups/{}/'.format(self.pk),
            'group-detail',
            url_kwargs={'pk': self.pk}
        )

    def test_group_subscribe(self):
        self.assert_url_matches_view(
            views.groups.GroupSubscribe,
            '/groups/{}/subscribe/'.format(self.pk),
            'group-subscribe',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_create(self):
        self.assert_url_matches_view(
            views.discussions.DiscussionCreate,
            '/groups/{}/new-discussion/'.format(self.pk),
            'discussion-create',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_detail(self):
        self.assert_url_matches_view(
            views.discussions.DiscussionThread,
            '/groups/discussions/{}/'.format(self.pk),
            'discussion-thread',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_subscribe(self):
        self.assert_url_matches_view(
            views.discussions.DiscussionSubscribe,
            '/groups/discussions/{}/subscribe/'.format(self.pk),
            'discussion-subscribe',
            url_kwargs={'pk': self.pk}
        )

    def test_comment_upload_file(self):
        self.assert_url_matches_view(
            views.comments.CommentUploadFile,
            '/groups/discussions/{}/upload-file/'.format(self.pk),
            'comment-upload-file',
            url_kwargs={'pk': self.pk}
        )

    def test_comment_delete(self):
        self.assert_url_matches_view(
            views.comments.CommentDelete,
            '/groups/comments/{}/delete/'.format(self.pk),
            'comment-delete',
            url_kwargs={'pk': self.pk}
        )
