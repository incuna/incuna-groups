from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from incuna_mail import send

from ._helpers import CommentPostView, get_reply_address
from .. import forms, models


NEW_DISCUSSION_SUBJECT = apps.get_app_config('groups').new_discussion_subject


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
                    'site': get_current_site(self.request),
                    'protocol': 'https' if self.request.is_secure() else 'http',
                },
            )


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
