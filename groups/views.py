from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, ListView

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
        models.Comment.objects.create(
            body=form.cleaned_data['comment'],
            discussion=discussion,
            user=user,
        )
        self.pk = discussion.pk
        return super(DiscussionCreate, self).form_valid(form)


class DiscussionThread(CreateView):
    """Allow a user to read and comment on a Discussion."""
    model = models.Comment
    form_class = forms.AddComment
    subscribe_form_class = forms.DiscussionSubscribeForm
    template_name = 'groups/discussion_thread.html'

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        self.discussion = models.Discussion.objects.select_related('group').get(pk=pk)
        return super(DiscussionThread, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Display the comments attached to a given discussion, newest at the bottom."""
        return self.discussion.comments.all()

    def get_context_data(self, *args, **kwargs):
        """Attach the discussion and its existing comments to the context."""
        context = super(DiscussionThread, self).get_context_data(*args, **kwargs)
        discussion = self.discussion
        form = self.subscribe_form_class(user=self.request.user, discussion=discussion)
        context['comments'] = self.get_queryset()
        context['discussion'] = discussion
        context['group'] = discussion.group
        context['subscribe-form'] = form
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.discussion = self.discussion
        return super(DiscussionThread, self).form_valid(form)


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
