try:
    from unittest import mock
except ImportError:
    import mock

import datetime

import pytz
from django.core import mail
from django.core.urlresolvers import reverse
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from .. import models
from ..views import discussions


class TestDiscussionThread(Python2AssertMixin, RequestTestCase):
    view_class = discussions.DiscussionThread

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


class TestDiscussionCreate(RequestTestCase):
    view_class = discussions.DiscussionCreate

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

        method_path = 'groups.views.discussions.DiscussionCreate.email_subscribers'
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
        address_path = 'groups.views.discussions.get_reply_address'  # imports are weird
        with mock.patch(address_path, return_value=reply_address):
            view.email_subscribers(new_discussion)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'New discussion in {}'.format(group.name))
        self.assertEqual(email.to, [subscriber.email])
        self.assertEqual(email.reply_to, [reply_address])
        self.assertIn('A new discussion on "{}"'.format(new_discussion.name), email.body)
        self.assertIn(subscriber.get_full_name(), email.body)
        self.assertIn(first_comment.body, email.body)
        self.assertIn('http://testserver', email.body)
