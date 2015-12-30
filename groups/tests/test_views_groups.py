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
        group = factories.GroupFactory.create()

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=group.pk)
        self.assertEqual(response.status_code, 200)
        detail_object = response.context_data['group']
        self.assertEqual(group, detail_object)
