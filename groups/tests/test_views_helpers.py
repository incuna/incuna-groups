try:
    from unittest import mock
except ImportError:
    import mock

from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .utils import RequestTestCase
from ..views import _helpers as helpers


class TestGetReplyAddress(Python2AssertMixin, RequestTestCase):
    def test_get_reply_address(self):
        """
        Assert that the method returns `reply-{uuid}@{domain}`.

        Look for dollar signs ($) instead of colons in the UUID, because we've done some
        replace work to ensure the email address is legal.
        """
        request = self.create_request()
        discussion = factories.DiscussionFactory.create()

        domain = get_current_site(request).domain
        uuid_regex = r'[\d\w\-_$]*'  # A string of alphanumerics, `-`, `_`, and/or `$`
        self.assertRegex(
            helpers.get_reply_address(discussion, request.user, request),
            r'reply-{uuid}@{domain}'.format(uuid=uuid_regex, domain=domain)
        )


class TestCommentEmailMixin(RequestTestCase):
    def setUp(self):
        """Instantiate a minimal CommentEmailMixin object."""
        self.discussion = factories.DiscussionFactory.create()
        self.request = self.create_request()
        self.view_obj = helpers.CommentEmailMixin()
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

        users = helpers.CommentPostView.users_to_notify(comment)
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
        users_method_path = 'groups.views._helpers.CommentEmailMixin.users_to_notify'
        address_method_path = 'groups.views._helpers.get_reply_address'
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
        self.assertIn('http://testserver', email.body)


class TestCommentPostView(Python2AssertMixin, RequestTestCase):
    def setUp(self):
        """Instantiate a minimal CommentPostView object."""
        class TestView(helpers.CommentPostView):
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
