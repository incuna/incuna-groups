from operator import methodcaller

from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from .. import forms, models


class GroupList(ListView):
    """Show a top-level list of discussion groups."""
    model = models.Group
    template_name = 'groups/group_list.html'
    ordering = 'name'


class GroupDetail(ListView):
    """Show the discussions belonging to a group."""
    model = models.Discussion
    paginate_by = 5
    template_name = 'groups/group_detail.html'
    subscribe_form_class = forms.SubscribeForm

    def dispatch(self, request, *args, **kwargs):
        """Get the group object we're accessing according to the pk in the URL."""
        self.group = get_object_or_404(models.Group, pk=self.kwargs['pk'])
        return super(GroupDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return all discussions on the particular group we're using."""
        return super(GroupDetail, self).get_queryset().filter(group=self.group)

    def sort_object_list(self, object_list):
        """
        Order the list of discussions by time of most recent update.

        Since this sorting irreversibly turns a queryset into a list, it's been separated
        from get_queryset() to allow for extensibility on the latter.
        """
        return sorted(object_list, key=methodcaller('get_date_updated'), reverse=True)

    def get_context_data(self, *args, **kwargs):
        """Sort the object list and allow the group to be displayed properly."""
        context = super(GroupDetail, self).get_context_data(*args, **kwargs)
        context['object_list'] = self.sort_object_list(context['object_list'])
        context['group'] = self.group
        context['group-subscribe-form'] = self.subscribe_form_class(
            user=self.request.user,
            instance=self.group,
            url_name='group-subscribe',
        )
        return context
