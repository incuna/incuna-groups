from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from .. import forms, models


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
