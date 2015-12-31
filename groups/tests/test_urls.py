from incuna_test_utils.testcases.urls import URLTestCase

from ..views import comments, discussions, groups, subscriptions


class TestGroupUrls(URLTestCase):
    pk = 42

    def test_group_list(self):
        self.assert_url_matches_view(
            groups.GroupList,
            '/groups/',
            'group-list',
        )

    def test_group_detail(self):
        self.assert_url_matches_view(
            groups.GroupDetail,
            '/groups/{}/'.format(self.pk),
            'group-detail',
            url_kwargs={'pk': self.pk}
        )

    def test_group_subscribe(self):
        self.assert_url_matches_view(
            subscriptions.GroupSubscribe,
            '/groups/{}/subscribe/'.format(self.pk),
            'group-subscribe',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_create(self):
        self.assert_url_matches_view(
            discussions.DiscussionCreate,
            '/groups/{}/new-discussion/'.format(self.pk),
            'discussion-create',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_detail(self):
        self.assert_url_matches_view(
            discussions.DiscussionThread,
            '/groups/discussions/{}/'.format(self.pk),
            'discussion-thread',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_subscribe(self):
        self.assert_url_matches_view(
            subscriptions.DiscussionSubscribe,
            '/groups/discussions/{}/subscribe/'.format(self.pk),
            'discussion-subscribe',
            url_kwargs={'pk': self.pk}
        )

    def test_comment_post_with_attachment(self):
        self.assert_url_matches_view(
            comments.CommentPostWithAttachment,
            '/groups/discussions/{}/post-with-attachment/'.format(self.pk),
            'comment-post-with-attachment',
            url_kwargs={'pk': self.pk}
        )

    def test_comment_delete(self):
        self.assert_url_matches_view(
            comments.CommentDelete,
            '/groups/comments/{}/delete/'.format(self.pk),
            'comment-delete',
            url_kwargs={'pk': self.pk}
        )
