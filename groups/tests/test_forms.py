from incuna_test_utils.compat import Python2AssertMixin

from .utils import RequestTestCase
from .. import forms, models


class TestAddCommentForm(Python2AssertMixin, RequestTestCase):
    form = forms.AddComment
    model = models.Comment

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


class TestDiscussionSubscribeForm(Python2AssertMixin, RequestTestCase):
    form = forms.DiscussionSubscribeForm

    def test_form_fields(self):
        expected = ['subscribe']
        fields = self.form.base_fields.keys()
        self.assertCountEqual(fields, expected)

    def test_form_valid(self):
        form = self.form(data={})
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_initial(self):
        form = self.form(subscribe=True)
        self.assertTrue(form.initial['subscribe'])
        form = self.form(subscribe=False)
        self.assertFalse(form.initial['subscribe'])
