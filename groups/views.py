import json
import re

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView
from incuna_mail import send

from . import forms, models

NEW_DISCUSSION_SUBJECT = apps.get_app_config('groups').new_discussion_subject
NEW_COMMENT_SUBJECT = apps.get_app_config('groups').new_comment_subject


def get_reply_address(discussion, user, request):
    uuid = discussion.generate_reply_uuid(user)
    site = get_current_site(request)
    return 'reply-{}@{}'.format(uuid, site)


class GroupList(ListView):
    """Show a top-level list of discussion groups."""
    model = models.Group
    paginate_by = 5
    template_name = 'groups/group_list.html'


class GroupDetail(ListView):
    """Show the discussions belonging to a group."""
    model = models.Discussion
    paginate_by = 5
    template_name = 'groups/group_detail.html'
    subscribe_form_class = forms.SubscribeForm

    def get_queryset(self):
        return super(GroupDetail, self).get_queryset().filter(group=self.group)

    def get_context_data(self, *args, **kwargs):
        context = super(GroupDetail, self).get_context_data(*args, **kwargs)
        context['group'] = self.group
        context['group-subscribe-form'] = self.subscribe_form_class(
            user=self.request.user,
            instance=self.group,
            url_name='group-subscribe',
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(models.Group, pk=self.kwargs['pk'])
        return super(GroupDetail, self).dispatch(request, *args, **kwargs)


class SubscribeBase(SingleObjectMixin, FormView):
    form_class = forms.SubscribeForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SubscribeBase, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass the user to the form to check subscription state."""
        kwargs = super(SubscribeBase, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'instance': self.object,
            'url_name': self.subscribe_url_name,
        })
        return kwargs

    def form_valid(self, form):
        """Subscribe or unsubscribe the request user."""
        user = self.request.user

        if form.cleaned_data['subscribe']:
            self.object.subscribe(user)
        else:
            self.object.unsubscribe(user)

        return super(SubscribeBase, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class GroupSubscribe(SubscribeBase):
    model = models.Group
    template_name = 'groups/group_subscribe_button.html'
    subscribe_url_name = 'group-subscribe'


class DiscussionCreate(FormView):
    """Start a new discussion by writing its first comment."""
    form_class = forms.DiscussionCreate
    template_name = 'groups/discussion_form.html'

    def get_group(self):
        return get_object_or_404(models.Group, pk=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DiscussionCreate, self).get_context_data(*args, **kwargs)
        context['group'] = self.get_group()
        return context

    def get_success_url(self):
        return reverse('discussion-thread', kwargs={'pk': self.pk})

    def form_valid(self, form):
        user = self.request.user
        discussion = models.Discussion.objects.create(
            creator=user,
            group=self.get_group(),
            name=form.cleaned_data['name'],
        )
        discussion.subscribers.add(user)
        models.TextComment.objects.create(
            body=form.cleaned_data['comment'],
            discussion=discussion,
            user=user,
        )
        self.pk = discussion.pk
        self.email_subscribers(discussion)
        return super(DiscussionCreate, self).form_valid(form)

    def email_subscribers(self, discussion):
        """Notify all subscribers to the discussion's parent group, except its creator."""
        users = discussion.group.watchers.exclude(pk=self.request.user.pk)
        for user in users:
            send(
                to=user.email,
                subject=NEW_DISCUSSION_SUBJECT.format(group=discussion.group.name),
                template_name='groups/emails/new_discussion.txt',
                reply_to=get_reply_address(discussion, user, self.request),
                context={
                    'discussion': discussion,
                    'user': user,
                },
            )


class CommentEmailMixin:
    """A mixin for CreateViews and similar that build comments."""
    @staticmethod
    def users_to_notify(comment):
        """
        Return subscribers to the comment's discussion or its parent group.

        Exclude anyone who's explicitly ignored this discussion, and the person who
        posted the comment.
        """
        discussion = comment.discussion
        discussion_subscribers = discussion.subscribers.all()
        group_subscribers = discussion.group.watchers.exclude(
            ignored_discussions=discussion
        )

        all_subscribers = discussion_subscribers | group_subscribers
        return all_subscribers.exclude(pk=comment.user.pk)

    def email_subscribers(self, comment):
        """Notify all subscribers to the discussion or its group, except the poster."""
        users = self.users_to_notify(comment)
        for user in users:
            send(
                to=user.email,
                subject=NEW_COMMENT_SUBJECT.format(discussion=comment.discussion.name),
                template_name='groups/emails/new_comment.txt',
                reply_to=get_reply_address(comment.discussion, user, self.request),
                context={
                    'comment': comment,
                    'user': user,
                },
            )


class CommentPostView(CommentEmailMixin, CreateView):
    """
    Base class for views that post a comment to a particular discussion.

    Must be initialised with form_class and template_name attributes, as required by
    the superclass, CreateView.
    """
    model = models.BaseComment

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        self.discussion = models.Discussion.objects.select_related('group').get(pk=pk)
        return super(CommentPostView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Attach the discussion and its existing comments to the context."""
        context = super(CommentPostView, self).get_context_data(*args, **kwargs)
        context['discussion'] = self.discussion
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.discussion = self.discussion
        self.email_subscribers(form.instance)
        return super(CommentPostView, self).form_valid(form)


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


class DiscussionSubscribe(SubscribeBase):
    """Provide an endpoint for the subscribe/unsubscribe button."""
    model = models.Discussion
    template_name = 'groups/subscribe_button.html'
    subscribe_url_name = 'discussion-subscribe'


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
    def dispatch(self, request, *args, **kwargs):
        self.uuid = kwargs.pop('uuid')
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
        """Turn `reply-{uuid}@domain.com` into just `uuid`."""
        uuid_regex = r'(?P<uuid>[\w\d\-_:]+)'
        regex = r'reply-{}@{}'.format(uuid_regex, get_current_site(request))
        match = re.compile(regex).match(email)
        if not match:
            raise Http404

        return match.group('uuid')

    def post(self, request, *args, **kwargs):
        """Create a new comment to self.pk."""
        message = json.loads(request.body.decode())['message']
        uuid = self.extract_uuid_from_email(message['recipient'], request)
        target = self.get_uuid_data(uuid)

        content = message['stripped-text']
        comment = models.TextComment.objects.create(
            body=content,
            user=target['user'],
            discussion=target['discussion'],
        )
        self.email_subscribers(comment)
