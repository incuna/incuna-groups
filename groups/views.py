from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, ListView

from . import forms, models


class GroupList(ListView):
    model = models.Group
    paginate_by = 5
    template_name = 'groups/group_list.html'


class GroupDetail(ListView):
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
        discussion = models.Discussion.objects.create(
            creator=self.request.user,
            group=self.get_group(),
            name=form.cleaned_data['name'],
        )
        models.Comment.objects.create(
            body=form.cleaned_data['comment'],
            discussion=discussion,
            user=self.request.user,
        )
        self.pk = discussion.pk
        return super(DiscussionCreate, self).form_valid(form)


class DiscussionThread(CreateView):
    """
    Comment on a Discussion
    """
    model = models.Comment
    form_class = forms.AddComment
    template_name = 'groups/discussion_thread.html'

    def get_queryset(self):
        """Display only the comments attached to a given discussion,
        newest at the bottom.
        """
        return self.get_discussion().comments.all()

    def get_discussion(self):
        return models.Discussion.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        """
        Attach the discussion and its existing comments to the context, so
        they can be displayed.
        """
        context = super(DiscussionThread, self).get_context_data(*args, **kwargs)
        context['comments'] = self.get_queryset()
        context['discussion'] = self.get_discussion()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.discussion = self.get_discussion()
        return super(DiscussionThread, self).form_valid(form)


class DiscussionSubscribe(FormView):
    form_class = forms.DiscussionSubscribeForm
    template_name = 'groups/subscribe_button.html'

    def get_discussion(self):
        return get_object_or_404(models.Discussion, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        """
        Add a kwarg denoting whether the subscribe button will subscribe or
        unsubscribe the user from the attached discussion.
        """
        user = self.request.user
        discussion = self.get_discussion()
        subscribe = user not in discussion.subscribers.all()

        kwargs = super(DiscussionSubscribe, self).get_form_kwargs()
        kwargs['subscribe'] = subscribe
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        discussion = self.get_discussion()

        if form.cleaned_data['subscribe']:
            discussion.subscribers.add(user)
        else:
            discussion.subscribers.remove(user)

        return super(DiscussionSubscribe, self).form_valid(form)

    def get_success_url(self):
        return self.get_discussion().get_absolute_url()
