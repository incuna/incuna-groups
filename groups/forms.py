from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.urlresolvers import reverse_lazy

from . import models


class AddComment(forms.ModelForm):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'body',
        FormActions(
            Submit('submit', 'Post comment'),
        ),
    )

    class Meta:
        fields = ('body',)
        model = models.Comment


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


class DiscussionSubscribeForm(forms.Form):
    subscribe = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.action = reverse_lazy('discussion-subscribe')

    class Meta:
        fields = ('subscribe',)

    def __init__(self, *args, **kwargs):
        """
        Accept a value for the 'subscribe' variable, and build the layout
        to reflect the action the form will take.
        """
        to_subscribe = kwargs.pop('subscribe', True)

        # setdefault is like 'get', but if it misses, puts the specified
        # default into kwargs and returns *that* object.
        initial_values = kwargs.setdefault('initial', {})
        initial_values['subscribe'] = to_subscribe

        super(DiscussionSubscribeForm, self).__init__(*args, **kwargs)

        button_text = 'Subscribe' if to_subscribe else 'Unsubscribe'
        self.helper.layout = Layout(
            FormActions(
                Submit('submit', button_text),
            ),
        )
