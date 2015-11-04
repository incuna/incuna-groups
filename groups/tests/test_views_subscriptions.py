from django.core.urlresolvers import reverse
from django_webtest import WebTest

from . import factories
from .utils import RequestTestCase
from ..views import subscriptions


class TestDiscussionSubscribe(RequestTestCase):
    view_class = subscriptions.DiscussionSubscribe

    def test_form_subscribe(self):
        discussion = factories.DiscussionFactory.create()
        user = self.user_factory.create()

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', user=user, data={'subscribe': True})
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that the user is now subscribed.
        self.assertIn(user, discussion.subscribers.all())
        self.assertIn(discussion, user.subscribed_discussions.all())

    def test_form_unsubscribe(self):
        discussion = factories.DiscussionFactory.create()
        user = self.user_factory.create()

        # Subscribe the user.
        discussion.subscribers.add(user)

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', user=user, data={'subscribe': False})
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that the user is now unsubscribed.
        self.assertNotIn(user, discussion.subscribers.all())
        self.assertNotIn(discussion, user.subscribed_discussions.all())


class TestGroupSubscribe(RequestTestCase):
    def setUp(self):
        self.view = subscriptions.GroupSubscribe.as_view()

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
