import datetime

try:
    from unittest import mock
except ImportError:
    import mock

import pytz
from django.core.urlresolvers import reverse
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


class TestCommentPostView(Python2AssertMixin, RequestTestCase):
    view_class = views.CommentPostView

    def setUp(self):
        """Instantiate a minimal CommentPostView object."""
        self.discussion = factories.DiscussionFactory.create()
        self.request = self.create_request()
        self.view_obj = self.view_class(
            request=self.request,
            kwargs={'pk': self.discussion.pk},
        )

        self.view_obj.dispatch(self.request)

    def test_dispatch(self):
        """After dispatch (called during setUp) the discussion is attached to the view."""
        self.assertEqual(self.view_obj.discussion, self.discussion)

    def test_includes_discussion(self):
        """Assert that the discussion is picked up and output."""
        context_data = self.view_obj.get_context_data()
        self.assertEqual(context_data['discussion'], self.discussion)

    def test_form_valid(self):
        """Assert that the request user and discussion are attached to the instance."""
        form = mock.MagicMock(instance=mock.MagicMock())
        self.view_obj.form_valid(form)
        self.assertEqual(form.instance.user, self.request.user)
        self.assertEqual(form.instance.discussion, self.discussion)


class TestDiscussionThread(Python2AssertMixin, RequestTestCase):
    view_class = views.DiscussionThread

    def make_datetime(self, year, month, day):
        return datetime.datetime(year, month, day, tzinfo=pytz.utc)

    def test_get(self):
        discussion = factories.DiscussionFactory.create()
        comment = factories.TextCommentFactory.create(discussion=discussion)
        factories.TextCommentFactory.create()

        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=discussion.pk)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context_data['comments'], [comment])
        self.assertEqual(response.context_data['discussion'], discussion)

    def test_sorting(self):
        discussion = factories.DiscussionFactory.create()
        newer_comment = factories.TextCommentFactory.create(
            discussion=discussion,
            date_created=self.make_datetime(2014, 1, 3)
        )
        older_comment = factories.TextCommentFactory.create(
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
        data = {'body': 'I am a comment!'}

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', user=user, data=data)
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that one comment was created with the appropriate properties.
        created_comment = models.TextComment.objects.get(discussion=discussion)
        self.assertEqual(created_comment.body, data['body'])
        self.assertEqual(created_comment.discussion, discussion)
        self.assertEqual(created_comment.user, user)


class TestCommentUploadFile(Python2AssertMixin, RequestTestCase):
    view_class = views.CommentUploadFile

    def make_datetime(self, year, month, day):
        return datetime.datetime(year, month, day, tzinfo=pytz.utc)

    def test_get(self):
        discussion = factories.DiscussionFactory.create()
        request = self.create_request()
        view = self.view_class.as_view()

        response = view(request, pk=discussion.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['discussion'], discussion)

    def test_post(self):
        discussion = factories.DiscussionFactory.create()
        file = factories.FileCommentFactory.build().file.file
        data = {'file': file}

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', data=data)
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that one comment was created with the appropriate properties.
        created_comment = models.FileComment.objects.get(discussion=discussion)
        self.assertEqual(created_comment.discussion, discussion)
        self.assertEqual(created_comment.user, request.user)


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

        discussion = models.Discussion.objects.get()  # will explode if it doesn't exist
        self.assertEqual(discussion.creator, user)
        self.assertEqual(discussion.subscribers.get(), user)
        self.assertEqual(discussion.comments.get().body, 'Super sensible comment.')

        self.assertEqual(response.status_code, 302)
        expected = reverse('discussion-thread', kwargs={'pk': discussion.pk})
        self.assertEqual(response['Location'], expected)


class TestDiscussionSubscribe(RequestTestCase):
    view_class = views.DiscussionSubscribe

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


class TestCommentDelete(RequestTestCase):
    view_class = views.CommentDelete

    def setUp(self):
        self.comment = factories.TextCommentFactory.create()
        self.request = self.create_request(user=self.comment.user)

    def test_get(self):
        view = self.view_class.as_view()
        response = view(self.request, pk=self.comment.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], self.comment)

    def test_get_forbidden(self):
        """A user who isn't allowed to delete the comment sees an error message."""
        view = self.view_class.as_view()
        request = self.create_request()
        response = view(request, pk=self.comment.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], self.comment.discussion.get_absolute_url())
        self.assertEqual(
            'You do not have permission to delete this comment.',
            request._messages.store[0]
        )

    def test_post(self):
        """POSTing to this endpoint deletes the comment."""
        view = self.view_class.as_view()
        self.request.method = 'post'
        response = view(self.request, pk=self.comment.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], self.comment.get_absolute_url())

        updated_comment = models.TextComment.objects.get(pk=self.comment.pk)
        self.assertTrue(updated_comment.is_deleted())

    def test_post_forbidden(self):
        """A user who isn't allowed to delete the comment sees an error message."""
        view = self.view_class.as_view()
        request = self.create_request('post')
        response = view(request, pk=self.comment.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], self.comment.discussion.get_absolute_url())
        self.assertEqual(
            'You do not have permission to delete this comment.',
            request._messages.store[0]
        )

    def test_delete(self):
        view_obj = self.view_class(request=self.request, kwargs={'pk': self.comment.pk})
        view_obj.comment = self.comment

        view_obj.delete(self.request)
        self.assertTrue(self.comment.is_deleted())

    def test_get_success_url(self):
        view_obj = self.view_class(request=self.request, kwargs={'pk': self.comment.pk})
        view_obj.comment = self.comment

        expected = self.comment.get_absolute_url()
        self.assertEqual(view_obj.get_success_url(), expected)
