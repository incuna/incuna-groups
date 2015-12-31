import datetime

from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from ..views import groups


class TestGroupList(Python2AssertMixin, RequestTestCase):
    view_class = groups.GroupList

    def test_get(self):
        group_last = factories.GroupFactory.create(name='zzzz')
        group_first = factories.GroupFactory.create(name='aaaa')

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request)
        self.assertEqual(response.status_code, 200)
        object_list = response.context_data['object_list']
        self.assertCountEqual(object_list, [group_first, group_last])


class TestGroupDetail(RequestTestCase):
    view_class = groups.GroupDetail

    def test_get(self):
        """
        Test that the right discussions are displayed in the right order.

        Discussions are shown in descending order of how recently they were updated, and
        only if they exist on the specified group.
        """
        group = factories.GroupFactory.create()
        factories.DiscussionFactory.create()  # An unrelated discussion - won't show up.
        discussion_oldest = factories.DiscussionFactory.create(group=group)
        discussion_newest = factories.DiscussionFactory.create(group=group)
        discussion_middle = factories.DiscussionFactory.create(group=group)
        factories.BaseCommentFactory.create(
            date_created=datetime.datetime(3970, 1, 1),
            discussion=discussion_newest,
        )
        factories.BaseCommentFactory.create(
            date_created=datetime.datetime(2970, 1, 1),
            discussion=discussion_middle,
        )
        factories.BaseCommentFactory.create(
            date_created=datetime.datetime(1970, 1, 1),
            discussion=discussion_oldest,
        )

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=group.pk)
        self.assertEqual(response.status_code, 200)
        detail_object = response.context_data['group']
        self.assertEqual(group, detail_object)

        discussions = response.context_data['object_list']
        expected = [discussion_newest, discussion_middle, discussion_oldest]
        self.assertSequenceEqual(discussions, expected)
