from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, ListView
from django.views.generic.edit import DeleteView

from . import forms, models


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

    def get_queryset(self):
        return super(GroupDetail, self).get_queryset().filter(group=self.group)

    def get_context_data(self, *args, **kwargs):
        context = super(GroupDetail, self).get_context_data(*args, **kwargs)
        context['group'] = self.group
        return context

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(models.Group, pk=self.kwargs['pk'])
        return super(GroupDetail, self).dispatch(request, *args, **kwargs)


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
        return super(DiscussionCreate, self).form_valid(form)


class CommentPostView(CreateView):
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
        return super(CommentPostView, self).form_valid(form)


class DiscussionThread(CommentPostView):
    """Allow a user to read and comment on a Discussion."""
    form_class = forms.AddTextComment
    subscribe_form_class = forms.DiscussionSubscribeForm
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
        form = self.subscribe_form_class(user=self.request.user, discussion=discussion)
        context['comments'] = self.get_queryset()
        context['group'] = discussion.group
        context['subscribe-form'] = form
        return context


class CommentUploadFile(CommentPostView):
    """Posts a file to a particular discussion."""
    form_class = forms.AddFileComment
    template_name = 'groups/comment_upload_file.html'


class DiscussionSubscribe(FormView):
    """Provide an endpoint for the subscribe/unsubscribe button."""
    form_class = forms.DiscussionSubscribeForm
    template_name = 'groups/subscribe_button.html'

    def dispatch(self, request, *args, **kwargs):
        self.discussion = get_object_or_404(models.Discussion, pk=self.kwargs['pk'])
        return super(DiscussionSubscribe, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DiscussionSubscribe, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'discussion': self.discussion,
        })
        return kwargs

    def form_valid(self, form):
        user = self.request.user

        if form.cleaned_data['subscribe']:
            self.discussion.subscribers.add(user)
        else:
            self.discussion.subscribers.remove(user)

        return super(DiscussionSubscribe, self).form_valid(form)

    def get_success_url(self):
        return self.discussion.get_absolute_url()


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
