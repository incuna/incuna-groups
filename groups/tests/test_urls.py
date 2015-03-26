from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestGroupUrls(URLTestCase):
    pk = 42

    def test_group_list(self):
        self.assert_url_matches_view(
            views.GroupList,
            '/groups/',
            'group-list',
        )

    def test_group_detail(self):
        self.assert_url_matches_view(
            views.GroupDetail,
            '/groups/{}/'.format(self.pk),
            'group-detail',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_create(self):
        self.assert_url_matches_view(
            views.DiscussionCreate,
            '/groups/{}/new-discussion/'.format(self.pk),
            'discussion-create',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_detail(self):
        self.assert_url_matches_view(
            views.DiscussionThread,
            '/groups/discussions/{}/'.format(self.pk),
            'discussion-thread',
            url_kwargs={'pk': self.pk}
        )

    def test_discussion_subscribe(self):
        self.assert_url_matches_view(
            views.DiscussionSubscribe,
            '/groups/discussions/{}/subscribe/'.format(self.pk),
            'discussion-subscribe',
            url_kwargs={'pk': self.pk}
        )
