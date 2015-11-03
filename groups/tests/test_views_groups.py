from django.core.urlresolvers import reverse
from django_webtest import WebTest
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from ..views import groups


class TestGroupList(Python2AssertMixin, RequestTestCase):
    view_class = groups.GroupList

    def test_get(self):
        groups = factories.GroupFactory.create_batch(2)

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request)
        self.assertEqual(response.status_code, 200)
        object_list = response.context_data['object_list']
        self.assertCountEqual(groups, object_list)


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


class TestGroupSubscribe(RequestTestCase):
    def setUp(self):
        self.view = groups.GroupSubscribe.as_view()

    def test_form_subscribe(self):
        group = factories.GroupFactory.create()
        request = self.create_request('post', data={'subscribe': True})

        response = self.view(request, pk=group.pk)

        self.assertEqual(response.status_code, 302)
        self.assertIn(request.user, group.watchers.all())
        self.assertIn(group, request.user.watched_groups.all())

    def test_form_unsubscribe(self):
        group = factories.GroupFactory.create()
        request = self.create_request('post', data={'subscribe': False})
        group.watchers.add(request.user)

        response = self.view(request, pk=group.pk)

        self.assertEqual(response.status_code, 302)
        self.assertNotIn(request.user, group.watchers.all())
        self.assertNotIn(group, request.user.watched_groups.all())


class TestGroupSubscribeIntegration(WebTest):
    def setUp(self):
        self.user = factories.UserFactory.create()
        self.group = factories.GroupFactory.create()
        self.group_url = reverse('group-detail', kwargs={'pk': self.group.pk})

    def test_subscribe_unsubscribe(self):
        """A user can subscribe and unsubscribe from a group."""
        # A user is subscribed to the group if they click the button
        self.app.get(self.group_url, user=self.user).form.submit()
        self.assertIn(self.user, self.group.watchers.all())

        # A user is unsubscribed from the group if they click the button
        self.app.get(self.group_url, user=self.user).form.submit()
        self.assertNotIn(self.user, self.group.watchers.all())
