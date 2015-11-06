import re

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.views.generic.edit import DeleteView

from ._helpers import CommentEmailMixin, CommentPostView
from .. import forms, models

NEW_COMMENT_SUBJECT = apps.get_app_config('groups').new_comment_subject


class DiscussionThread(CommentPostView):
    """Allow a user to read and comment on a Discussion."""
    form_class = forms.AddTextComment
    subscribe_form_class = forms.SubscribeForm
    template_name = 'groups/discussion_thread.html'

    def get_queryset(self):
        """
        Display the comments attached to a given discussion, newest at the bottom.

        Use the CommentManager's with_user_may_delete method to annotate each comment
        with a value denoting if it can be deleted by the current user. This allows us
        to conditionally display the delete link in the template.
        """
        return self.discussion.comments.with_user_may_delete(self.request.user)

    def get_context_data(self, *args, **kwargs):
        """Attach the discussion and its existing comments to the context."""
        context = super(DiscussionThread, self).get_context_data(*args, **kwargs)
        discussion = self.discussion
        form = self.subscribe_form_class(
            user=self.request.user,
            instance=discussion,
            url_name='discussion-subscribe',
        )
        context['comments'] = self.get_queryset()
        context['group'] = discussion.group
        context['discussion-subscribe-form'] = form
        return context


class CommentUploadFile(CommentPostView):
    """Posts a file to a particular discussion."""
    form_class = forms.AddFileComment
    template_name = 'groups/comment_upload_file.html'


class CommentDelete(DeleteView):
    """
    Deletes a particular comment after confirming with an 'Are you sure?' page.

    Rather than fully deleting the comment, set its state to DELETED so it continues to
    exist but displays differently.
    """
    model = models.BaseComment
    template_name = 'groups/comment_delete.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Disallow access to any user other than admins or the comment creator.

        On unauthorised access, kick the user back to the discussion they came from with
        a Django message displayed.  Don't scroll down to the comment, otherwise they
        might not see the message.
        """
        self.comment = self.get_object()
        if not self.comment.may_be_deleted(request.user):
            messages.error(request, 'You do not have permission to delete this comment.')
            return HttpResponseRedirect(self.comment.discussion.get_absolute_url())

        return super(CommentDelete, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.comment.delete_state()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.comment.get_absolute_url()


class CommentPostByEmail(CommentEmailMixin, View):
    """
    Receive comments posted by email and create them in the database.

    This view is intended to be linked to an endpoint that provides an URL kwarg
    'uuid'.  This matches up to an EmailUUID object that stores the discussion and user
    being used.
    """
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CommentPostByEmail, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get_uuid_data(uuid):
        """Unwrap the discussion and user data in the UUID string."""
        data = signing.loads(uuid)
        return {
            'discussion': get_object_or_404(models.Discussion, pk=data['discussion_pk']),
            'user': get_object_or_404(get_user_model(), pk=data['user_pk'])
        }

    @staticmethod
    def extract_uuid_from_email(email, request):
        """
        Turn `reply-{uuid}@domain.com` into just `uuid`.

        The UUIDs contain colons, which aren't allowed in email addresses, so they get
        replaced with dollar signs in the `reply-to` address.  We have to undo that here.
        """
        uuid_regex = r'(?P<uuid>[\w\d\-_$]+)'
        regex = r'reply-{}@{}'.format(uuid_regex, get_current_site(request))
        match = re.compile(regex).match(email)
        if not match:
            raise Http404

        return match.group('uuid').replace('$', ':')

    @staticmethod
    def create_file_comments(request, user, discussion):
        """
        Create any number of file comments from the attachments in this message.

        Mailgun provides an entry called `attachment-count` to store the number
        of attachments, then each attachment is a separate entry, `attachment-x` where
        `x` is a number.
        """
        for attachment in request.FILES.values():
            models.FileComment.objects.create(
                file=attachment,
                user=user,
                discussion=discussion,
            )

    def post(self, request, *args, **kwargs):
        """Create a new comment to self.pk."""
        message = request.POST
        uuid = self.extract_uuid_from_email(message['recipient'], request)
        target = self.get_uuid_data(uuid)

        user = target['user']
        discussion = target['discussion']

        self.create_file_comments(request, user, discussion)

        content = message['stripped-text']
        comment = models.TextComment.objects.create(
            body=content,
            user=user,
            discussion=discussion,
        )
        self.email_subscribers(comment)

        return HttpResponse(status=200)
