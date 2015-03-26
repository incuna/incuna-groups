import datetime

import pytz
from django.core.urlresolvers import reverse
from django.http import Http404
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from .. import models, views


class TestGroupList(Python2AssertMixin, RequestTestCase):
    view_class = views.GroupList

    def test_get(self):
        groups = factories.GroupFactory.create_batch(2)

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request)
        self.assertEqual(response.status_code, 200)
        object_list = response.context_data['object_list']
        self.assertCountEqual(groups, object_list)


class TestGroupDetail(RequestTestCase):
    view_class = views.GroupDetail

    def test_get(self):
        group = factories.GroupFactory.create()

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=group.pk)
        self.assertEqual(response.status_code, 200)
        detail_object = response.context_data['group']
        self.assertEqual(group, detail_object)


class TestDiscussionThread(Python2AssertMixin, RequestTestCase):
    view_class = views.DiscussionThread

    def make_datetime(self, year, month, day):
        return datetime.datetime(year, month, day, tzinfo=pytz.utc)

    def test_get(self):
        discussion = factories.DiscussionFactory.create()
        comment = factories.CommentFactory.create(discussion=discussion)
        factories.CommentFactory.create()

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=discussion.pk)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context_data['comments'], [comment])
        self.assertEqual(response.context_data['discussion'], discussion)

    def test_sorting(self):
        discussion = factories.DiscussionFactory.create()
        newer_comment = factories.CommentFactory.create(
            discussion=discussion,
            date_created=self.make_datetime(2014, 1, 3)
        )
        older_comment = factories.CommentFactory.create(
            discussion=discussion,
            date_created=self.make_datetime(2014, 1, 1)
        )

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=discussion.pk)
        self.assertEqual(response.status_code, 200)
        comments = [older_comment, newer_comment]
        self.assertCountEqual(response.context_data['comments'], comments)
        self.assertEqual(response.context_data['discussion'], discussion)

    def test_post(self):
        discussion = factories.DiscussionFactory.create()
        user = self.user_factory.create()
        data = {
            'body': 'I am a comment!'
        }

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', user=user, data=data)
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that one comment was created with the appropriate properties.
        created_comment = models.Comment.objects.get(discussion=discussion)
        self.assertEqual(created_comment.body, data['body'])
        self.assertEqual(created_comment.discussion, discussion)
        self.assertEqual(created_comment.user, user)


class TestDiscussionCreate(RequestTestCase):
    view_class = views.DiscussionCreate

    def test_get(self):
        group = factories.GroupFactory.create()

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=group.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['group'], group)

    def test_post(self):
        group = factories.GroupFactory.create()
        user = self.user_factory.create()
        data = {
            'creator': user,
            'group': group,
            'name': 'Super Sensible Discussion',
            'comment': 'Super sensible comment.',
        }

        self.assertFalse(models.Discussion.objects.exists())

        request = self.create_request('post', user=user, data=data)
        view = self.view_class.as_view()
        response = view(request, pk=group.pk)

        discussion = models.Discussion.objects.all()
        self.assertEqual(len(discussion), 1)

        self.assertEqual(response.status_code, 302)
        expected = reverse('discussion-thread', kwargs={'pk': discussion[0].pk})
        self.assertEqual(response['Location'], expected)


class TestDiscussionSubscribe(RequestTestCase):
    view_class = views.DiscussionSubscribe

    def test_get_discussion(self):
        discussion = factories.DiscussionFactory.create()
        view = self.view_class()

        # Assert that the discussion is found.
        view.kwargs = {'pk': discussion.pk}
        self.assertEqual(discussion, view.get_discussion())

    def test_get_discussion_404(self):
        view = self.view_class()

        # Assert we get a 404 when we miss.
        view.kwargs = {'pk': 42424242}
        with(self.assertRaises(Http404)):
            view.get_discussion()

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

    def test_get_form_kwargs(self):
        discussion = factories.DiscussionFactory.create()
        user = self.user_factory.create()

        # Feed the correct data into the view, so we can call get_form_kwargs.
        request = self.create_request('get', user=user)
        view = self.view_class()
        view.request = request
        view.kwargs = {'pk': discussion.pk}

        # With an unsubscribed user, hitting this view should return
        # subscribe=True.
        self.assertTrue(view.get_form_kwargs()['subscribe'])

        # Subscribe the user, then check again.  We should return
        # subscribe=False now.
        discussion.subscribers.add(user)
        self.assertFalse(view.get_form_kwargs()['subscribe'])
