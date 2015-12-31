try:
    from unittest import mock
except ImportError:
    import mock

import datetime

import pytz
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import Http404
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from .. import models
from ..views import comments


class TestCommentPostWithAttachment(Python2AssertMixin, RequestTestCase):
    view_class = comments.CommentPostWithAttachment

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
        uploadable_file = factories.AttachedFileFactory.build().file.file
        body = 'I am a comment'
        data = {'body': body, 'file': uploadable_file}

        # Hit the view, passing in the necessaries.
        request = self.create_request('post', data=data)
        view = self.view_class.as_view()
        view(request, pk=discussion.pk)

        # Assert that one comment was created with the appropriate properties.
        created_comment = models.TextComment.objects.get(discussion=discussion)
        self.assertEqual(created_comment.discussion, discussion)
        self.assertEqual(created_comment.user, request.user)

        # The comment also has one attachment containing the uploaded file.
        # We can't directly test for file equality (since it gets copied under a
        # different name) but we can assert both files have the same size as an
        # approximation.
        attachment = created_comment.attachments.get()
        self.assertEqual(attachment.user, request.user)
        self.assertEqual(attachment.file.file.size, uploadable_file.size)


class TestCommentDelete(RequestTestCase):
    view_class = comments.CommentDelete

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
    view_class = comments.CommentPostByEmail

    # Some method paths for mocking out helpers.
    extract_path = 'groups.views.comments.CommentPostByEmail.extract_uuid_from_email'
    uuid_path = 'groups.views.comments.CommentPostByEmail.get_uuid_data'
    email_path = 'groups.views.comments.CommentEmailMixin.email_subscribers'
    file_create_path = 'groups.views.comments.CommentPostByEmail.create_file_attachments'

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
        """
        Assert that `reply-{uuid}@{domain}` becomes `uuid`.

        The UUID that is returned has had its dollar signs turned back into colons so
        that it can be parsed properly.
        """
        reply_uuid = 'I-aM$an_UU1D'
        expected_uuid = reply_uuid.replace('$', ':')
        request = self.create_request()
        domain = get_current_site(request).domain
        email = 'reply-{}@{}'.format(reply_uuid, domain)

        extracted_uuid = self.view_class.extract_uuid_from_email(email, request)
        self.assertEqual(extracted_uuid, expected_uuid)

    def test_extract_uuid_failure(self):
        """The method throws a 404 when it fails."""
        with self.assertRaises(Http404):
            self.view_class.extract_uuid_from_email(
                'will-this-work@example.com',
                self.create_request()
            )

    def test_create_file_attachments(self):
        """Assert that an AttachedFile is created for each attachment in request.FILES."""
        comment = factories.TextCommentFactory.create()
        attached_file = factories.AttachedFileFactory.build().file
        request = mock.MagicMock(FILES={'attachment-1': attached_file})

        self.view_class.create_file_attachments(request, comment.user, comment)
        self.assertTrue(
            models.AttachedFile.objects.filter(
                file=attached_file,
                user=comment.user,
                attached_to=comment,
            ).exists()
        )

    def test_post(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        uuid_data = {'discussion': discussion, 'user': user}

        message_body = 'Email replying is so straightforward and fun'
        request_data = {
            'stripped-text': message_body,
            'recipient': 'this is needed, but mocked out',
        }

        request = self.create_request(
            method='post',
            content_type='application/json',
        )
        request.POST = request_data
        view = self.view_class.as_view()

        # Mock out all the helper methods, since they're tested separately, and it saves
        # on creating a *ton* of extra setup data.  There doesn't appear to be a way to
        # achieve this without extremely nested `with` statements.
        with mock.patch(self.extract_path, return_value='uuid') as extract_uuid:
            with mock.patch(self.uuid_path, return_value=uuid_data):
                with mock.patch(self.email_path) as email_subscribers:
                    with mock.patch(self.file_create_path) as create_file_attachments:
                        response = view(request, uuid='use of this is mocked out')

        # Mailgun likes to receive confirmation, so it's important we send a HTTP200 to
        # avoid resends.
        self.assertEqual(response.status_code, 200)

        # Assert that a comment was created correctly.
        comment = models.TextComment.objects.get()
        self.assertEqual(comment.body, message_body)

        # Assert that we've respected the recipient when generating the UUID, created
        # file comments out of any attachments, and emailed any subscribers.
        extract_uuid.assert_called_once_with(request_data['recipient'], request)
        create_file_attachments.assert_called_once_with(request, user, comment)
        email_subscribers.assert_called_once_with(comment)
