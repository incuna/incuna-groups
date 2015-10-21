from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.urlresolvers import reverse_lazy

from . import models


class BaseAddCommentForm(forms.ModelForm):
    """A base class for forms that create models inheriting from BaseComment."""
    def __init__(self, *args, **kwargs):
        super(BaseAddCommentForm, self).__init__(*args, **kwargs)
        self.helper = self.build_helper()

    def build_helper(self):
        """An overridable method that creates a crispy_forms layout helper."""
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-8'
        helper.layout = Layout(
            'body',
            FormActions(
                Submit('comment-submit', 'Post comment'),
            ),
        )
        return helper

    class Meta:
        fields = ('body',)


class AddTextComment(BaseAddCommentForm):
    """A form that posts TextComments."""
    class Meta(BaseAddCommentForm.Meta):
        model = models.TextComment


class AddFileComment(BaseAddCommentForm):
    """A form that uploads FileComments."""
    def build_helper(self):
        helper = super(AddFileComment, self).build_helper()
        helper.layout = Layout(
            'file',
            FormActions(
                Submit('comment-submit', 'Upload this file'),
            ),
        )
        return helper

    class Meta:
        fields = ('file',)
        model = models.FileComment


class DiscussionCreate(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
    name = forms.CharField(max_length=255)
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'name',
        'comment',
        FormActions(
            Submit('submit', 'Create Discussion'),
        ),
    )


class SubscribeFormMixin(object):
    subscribe = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, instance, *args, **kwargs):
        to_subscribe = self.to_subscribe(user, instance)
        initial_values = kwargs.setdefault('initial', {})
        initial_values['subscribe'] = to_subscribe

        super(SubscribeFormMixin, self).__init__(*args, **kwargs)

        button_text = 'Subscribe' if to_subscribe else 'Unsubscribe'

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            FormActions(
                Submit('subscribe-submit', button_text),
            ),
        )
        self.helper.form_action = reverse_lazy(
            self.subscribe_url_name,
            kwargs={'pk': instance.pk},
        )


class GroupSubscribeForm(SubscribeFormMixin, forms.ModelForm):
    subscribe_url_name = 'group-subscribe'

    class Meta:
        model = models.Group
        fields = ()

    def to_subscribe(self, user, group):
        return not group.watchers.filter(id=user.pk).exists()


class DiscussionSubscribeForm(SubscribeFormMixin, forms.Form):
    subscribe_url_name = 'discussion-subscribe'

    def to_subscribe(self, user, discussion):
        return not discussion.subscribers.filter(id=user.pk).exists()
