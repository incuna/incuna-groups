from bs4 import BeautifulSoup
from crispy_forms.utils import render_crispy_form
from incuna_test_utils.compat import Python2AssertMixin
from incuna_test_utils.factories.images import uploadable_file

from . import factories
from .utils import RequestTestCase
from .. import forms, models


def has_submit(form):
    rendered_form = render_crispy_form(form)
    parser = BeautifulSoup(rendered_form, 'html.parser')
    submits = parser.findAll('input', {'type': 'submit'})
    return any(submits)


def get_button(form):
    rendered_form = render_crispy_form(form)
    return BeautifulSoup(rendered_form, 'html.parser').findAll('button')[0]


class TestAddTextComment(Python2AssertMixin, RequestTestCase):
    form = forms.AddTextComment
    model = models.TextComment

    def test_form_fields(self):
        expected = ['body']
        fields = self.form.base_fields.keys()
        self.assertCountEqual(fields, expected)

    def test_form_valid(self):
        data = {'body': 'I am a comment'}
        form = self.form(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_not_valid(self):
        form = self.form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)

    def test_submit_not_input(self):
        """The form does not have a submit <input>."""
        form = self.form()
        self.assertFalse(has_submit(form))

    def test_submit_button(self):
        """
        The form has a submit <button>.

        This allows for more flexibility in styling.
        """
        button = get_button(self.form())
        self.assertEqual(button.get('type'), 'submit')


class TestAddTextCommentWithAttachment(Python2AssertMixin, RequestTestCase):
    form = forms.AddTextCommentWithAttachment
    model = models.TextComment

    def test_form_fields(self):
        expected = ['body', 'file']
        fields = self.form.base_fields.keys()
        self.assertCountEqual(fields, expected)

    def test_form_valid(self):
        data = {'body': 'I am a comment'}
        file_data = {'file': uploadable_file()}
        form = self.form(data=data, files=file_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_not_valid(self):
        form = self.form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)
        self.assertIn('file', form.errors)

    def test_submit_not_input(self):
        """The form does not have a submit <input>."""
        form = self.form()
        self.assertFalse(has_submit(form))

    def test_submit_button(self):
        """
        The form has a submit <button>.

        This allows for more flexibility in styling.
        """
        button = get_button(self.form())
        self.assertEqual(button.get('type'), 'submit')


class TestDiscussionCreateForm(Python2AssertMixin, RequestTestCase):
    form = forms.DiscussionCreate

    def test_form_fields(self):
        expected = ['name', 'comment']
        fields = self.form.base_fields.keys()
        self.assertCountEqual(fields, expected)

    def test_form_valid(self):
        data = {
            'name': "What's in a name?",
            'comment': 'First!!!!!!',
        }

        form = self.form(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_not_valid(self):
        form = self.form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_submit_not_input(self):
        """The form does not have a submit <input>."""
        form = self.form()
        self.assertFalse(has_submit(form))

    def test_submit_button(self):
        """
        The form has a submit <button>.

        This allows for more flexibility in styling.
        """
        button = get_button(self.form())
        self.assertEqual(button.get('type'), 'submit')


class TestSubscribeForm(Python2AssertMixin, RequestTestCase):
    form = forms.SubscribeForm

    def setUp(self):
        self.discussion = factories.DiscussionFactory.create()
        self.user = self.discussion.creator

    def get_form(self, **kwargs):
        return self.form(
            user=self.user,
            instance=self.discussion,
            url_name='discussion-subscribe',
            **kwargs
        )

    def test_form_valid(self):
        form = self.get_form(data={})
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_initial_subscribe(self):
        form = self.get_form()
        self.assertTrue(form.initial['subscribe'])

    def test_initial_unsubscribe(self):
        self.discussion.subscribers.add(self.user)
        form = self.get_form()
        self.assertFalse(form.initial['subscribe'])

    def test_submit_not_input(self):
        """The form does not have a submit <input>."""
        form = self.get_form()
        self.assertFalse(has_submit(form))

    def test_submit_button(self):
        """
        The form has a submit <button>.

        This allows for more flexibility in styling.
        """
        button = get_button(self.get_form())
        self.assertEqual(button.get('type'), 'submit')

    def test_button_text_subscribe(self):
        """The button says 'Subscribe' when the user is not subscribed."""
        button = get_button(self.get_form())
        self.assertEqual(button.string, 'Subscribe')

    def test_button_text_unsubscribe(self):
        """The button says 'Unsubscribe' when the user is subscribed."""
        self.discussion.subscribers.add(self.user)
        button = get_button(self.get_form())
        self.assertEqual(button.string, 'Unsubscribe')
