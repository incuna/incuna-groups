from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from .. import forms, models


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


class DiscussionSubscribe(SubscribeBase):
    """Provide an endpoint for the subscribe/unsubscribe button."""
    model = models.Discussion
    template_name = 'groups/subscribe_button.html'
    subscribe_url_name = 'discussion-subscribe'


class GroupSubscribe(SubscribeBase):
    model = models.Group
    template_name = 'groups/group_subscribe_button.html'
    subscribe_url_name = 'group-subscribe'
