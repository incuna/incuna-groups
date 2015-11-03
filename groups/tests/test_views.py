try:
    from unittest import mock
except ImportError:
    import mock

import datetime
import json

import pytz
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core import signing
from django.core.urlresolvers import reverse
from django.http import Http404
from django_webtest import WebTest
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from .. import models, views


class TestGetReplyAddress(Python2AssertMixin, RequestTestCase):
    def test_get_reply_address(self):
        """Assert that the method returns `reply-{uuid}@{domain}`."""
        request = self.create_request()
        discussion = factories.DiscussionFactory.create()

        domain = get_current_site(request).domain
        uuid_regex = r'[\d\w\-_:]*'  # A string of alphanumerics, `-`, `_`, and/or `:`
        self.assertRegex(
            views.get_reply_address(discussion, request.user, request),
            r'reply-{uuid}@{domain}'.format(uuid=uuid_regex, domain=domain)
        )


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


class TestGroupSubscribe(RequestTestCase):
    def setUp(self):
        self.view = views.GroupSubscribe.as_view()

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

    def test_subscribe_unsubscribe(self):
        """A user can subscribe and unsubscribe from a group."""
        group = factories.GroupFactory.create()
        group_url = reverse('group-detail', kwargs={'pk': group.pk})

        # A user not yet subscribed sees a Subscribe button
        form = self.app.get(group_url, user=self.user).form
        submit_button = form.fields['subscribe-submit'][0]
        self.assertEqual(submit_button._value, 'Subscribe')

        # A user is subscribed to the group if they click the button
        form.submit()
        self.assertIn(self.user, group.watchers.all())

        # A subscribed user sees an Unsubscribe button
        form = self.app.get(group_url, user=self.user).form
        submit_button = form.fields['subscribe-submit'][0]
        self.assertEqual(submit_button._value, 'Unsubscribe')

        # A user is unsubscribed from the group if they click the button
        form.submit()
        self.assertNotIn(self.user, group.watchers.all())


class TestCommentEmailMixin(RequestTestCase):
    def setUp(self):
        """Instantiate a minimal CommentEmailMixin object."""
        self.discussion = factories.DiscussionFactory.create()
        self.request = self.create_request()
        self.view_obj = views.CommentEmailMixin()
        self.view_obj.request = self.request

    def test_users_to_notify(self):
        """
        Test that users_to_notify picks the right users.

        * All subscribers to the discussion,
        * plus all subscribers to the discussion's parent group,
        * minus everyone who ignored the discussion,
        * minus the user who posted the comment.
        """
        (
            group_subscriber,  # Will be notified.
            discussion_subscriber,  # Will also be notified.
            discussion_ignorer,  # A group subscriber, but ignores the discussion = no.
            comment_poster,  # The poster isn't notified regardless of subscriptions.
            unrelated_user,  # Not subscribed at all = no notifications.
        ) = factories.UserFactory.create_batch(5)

        group = factories.GroupFactory.create()
        discussion = factories.DiscussionFactory.create(group=group)
        comment = factories.BaseCommentFactory.create(
            user=comment_poster,
            discussion=discussion,
        )

        # Set up the various subscription preferences as described above.
        group.watchers = [group_subscriber, discussion_ignorer, comment_poster]
        discussion.subscribers = [discussion_subscriber, comment_poster]
        discussion.ignorers = [discussion_ignorer]

        users = views.CommentPostView.users_to_notify(comment)
        self.assertEqual(set(users), {group_subscriber, discussion_subscriber})

    def test_email_subscribers(self):
        """
        Test notification emails for a new comment.

        The users_to_notify logic is tested above, so we can mock it here.  Same with
        get_reply_address, which is awkward to assert otherwise.
        """
        subscriber = factories.UserFactory.create()
        discussion = factories.DiscussionFactory.create()
        comment = factories.TextCommentFactory.create(discussion=discussion)

        reply_address = 'leeroy@jenkins.com'
        users_method_path = 'groups.views.CommentEmailMixin.users_to_notify'
        address_method_path = 'groups.views.get_reply_address'
        with mock.patch(users_method_path, return_value=[subscriber]):
            with mock.patch(address_method_path, return_value=reply_address):
                self.view_obj.email_subscribers(comment)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'New comment on {}'.format(discussion.name))
        self.assertEqual(email.to, [subscriber.email])
        self.assertEqual(email.reply_to, [reply_address])
        self.assertIn('A new comment has been posted', email.body)
        self.assertIn(subscriber.get_full_name(), email.body)
        self.assertIn(comment.body, email.body)


class TestCommentPostView(Python2AssertMixin, RequestTestCase):
    def setUp(self):
        """Instantiate a minimal CommentPostView object."""
        class TestView(views.CommentPostView):
            """Set fields attribute to fulfil ModelFormMixin requirements."""
            fields = ()

        self.discussion = factories.DiscussionFactory.create()
        self.request = self.create_request()
        self.view_obj = TestView(
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

        method_path = 'groups.views.DiscussionCreate.email_subscribers'
        with mock.patch(method_path) as email_subscribers:
            response = view(request, pk=group.pk)

        discussion = models.Discussion.objects.get()  # will explode if it doesn't exist
        self.assertEqual(discussion.creator, user)
        self.assertEqual(discussion.subscribers.get(), user)
        self.assertEqual(discussion.comments.get().body, 'Super sensible comment.')

        self.assertEqual(response.status_code, 302)
        expected = reverse('discussion-thread', kwargs={'pk': discussion.pk})
        self.assertEqual(response['Location'], expected)

        self.assertEqual(email_subscribers.call_count, 1)

    def test_email_subscribers(self):
        """
        Test notification emails for a new discussion.

        Assert that subscribers to a group are emailed correctly when a new discussion
        is posted there, apart from the discussion's creator.
        """
        group = factories.GroupFactory.create()
        subscriber = factories.UserFactory.create()
        creator = factories.UserFactory.create()
        group.subscribe(subscriber)
        group.subscribe(creator)

        new_discussion = factories.DiscussionFactory.create(creator=creator, group=group)
        first_comment = factories.TextCommentFactory.create(discussion=new_discussion)

        view = self.view_class()
        view.request = self.create_request(user=creator)

        reply_address = 'leeroy@jenkins.com'
        address_method_path = 'groups.views.get_reply_address'
        with mock.patch(address_method_path, return_value=reply_address):
            view.email_subscribers(new_discussion)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'New discussion in {}'.format(group.name))
        self.assertEqual(email.to, [subscriber.email])
        self.assertEqual(email.reply_to, [reply_address])
        self.assertIn('A new discussion "{}"'.format(new_discussion.name), email.body)
        self.assertIn(subscriber.get_full_name(), email.body)
        self.assertIn(first_comment.body, email.body)


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


class TestCommentPostByEmail(RequestTestCase):
    view_class = views.CommentPostByEmail

    # Some method paths for mocking out helpers.
    extract_method_path = 'groups.views.CommentPostByEmail.extract_uuid_from_email'
    uuid_method_path = 'groups.views.CommentPostByEmail.get_uuid_data'
    email_method_path = 'groups.views.CommentEmailMixin.email_subscribers'

    def generate_uuid(self, discussion_pk, user_pk):
        """Generate a UUID in the same way as a discussion."""
        data = {'discussion_pk': discussion_pk, 'user_pk': user_pk}
        return signing.dumps(data)

    def test_get_uuid_data(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        uuid = self.generate_uuid(discussion.pk, user.pk)

        data = self.view_class.get_uuid_data(uuid)
        expected_data = {'discussion': discussion, 'user': user}
        self.assertEqual(data, expected_data)

    def test_get_uuid_data_no_discussion(self):
        user = factories.UserFactory.create()
        uuid = self.generate_uuid(42, user.pk)

        with self.assertRaises(Http404):
            self.view_class.get_uuid_data(uuid)

    def test_get_uuid_data_no_user(self):
        discussion = factories.DiscussionFactory.create()
        uuid = self.generate_uuid(discussion.pk, 42)

        with self.assertRaises(Http404):
            self.view_class.get_uuid_data(uuid)

    def test_extract_uuid_from_email(self):
        """Assert that `reply-{uuid}@{domain}` becomes `uuid`."""
        uuid = 'I-aM:an_UU1D'
        request = self.create_request()
        domain = get_current_site(request).domain
        email = 'reply-{}@{}'.format(uuid, domain)

        extracted_uuid = self.view_class.extract_uuid_from_email(email, request)
        self.assertEqual(extracted_uuid, uuid)

    def test_extract_uuid_failure(self):
        """The method throws a 404 when it fails."""
        with self.assertRaises(Http404):
            self.view_class.extract_uuid_from_email(
                'will-this-work@example.com',
                self.create_request()
            )

    def test_post(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        uuid_data = {'discussion': discussion, 'user': user}

        message_body = 'Email replying is so straightforward and fun'
        request_data = {
            'message': {
                'stripped-text': message_body,
                'recipient': 'this is needed, but mocked out',
            }
        }

        request = self.create_request(
            method='post',
            data=json.dumps(request_data),
            content_type='application/json',
        )
        view = self.view_class.as_view()

        with mock.patch(self.extract_method_path, return_value='uuid') as extract_uuid:
            with mock.patch(self.uuid_method_path, return_value=uuid_data):
                with mock.patch(self.email_method_path) as email_subscribers:
                    view(request, uuid='use of this is mocked out')

        # Assert that a comment was created, subscribers were emailed, and the
        # recipient field in the request data was respected.
        comment = models.TextComment.objects.get()
        self.assertEqual(comment.body, message_body)
        email_subscribers.assert_called_once_with(comment)
        extract_uuid.assert_called_once_with(
            request_data['message']['recipient'],
            request
        )
