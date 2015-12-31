from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
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
                StrictButton('Post comment', type='submit'),
            ),
        )
        return helper

    class Meta:
        fields = ('body',)


class AddTextComment(BaseAddCommentForm):
    """A form that posts TextComments."""
    class Meta(BaseAddCommentForm.Meta):
        model = models.TextComment


class AddTextCommentWithAttachment(BaseAddCommentForm):
    file = forms.FileField()

    def build_helper(self):
        helper = super(AddTextCommentWithAttachment, self).build_helper()
        helper.layout = Layout(
            'body',
            'file',
            FormActions(
                StrictButton('Upload and post', type='submit'),
            ),
        )
        return helper

    class Meta:
        model = models.TextComment
        fields = ('body', 'file',)
        labels = {
            'body': 'Comment',
            'file': 'Attachment',
        }


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
            StrictButton('Create Discussion', type='submit'),
        ),
    )


class SubscribeForm(forms.Form):
    subscribe = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        fields = ('subscribe',)

    def __init__(self, user, instance, url_name, *args, **kwargs):
        """
        Build the layout to reflect the action the form will take.

        Accepts (and requires) a user and an instance being subscribed to
        as keyword arguments.
        """
        to_subscribe = not instance.is_subscribed(user)
        initial_values = kwargs.setdefault('initial', {})
        initial_values['subscribe'] = to_subscribe

        super(SubscribeForm, self).__init__(*args, **kwargs)

        button_text = 'Subscribe' if to_subscribe else 'Unsubscribe'

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            FormActions(
                StrictButton(button_text, type='submit'),
            ),
        )
        self.helper.form_action = reverse_lazy(url_name, kwargs={'pk': instance.pk})
