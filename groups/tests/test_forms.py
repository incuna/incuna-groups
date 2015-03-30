from incuna_test_utils.compat import Python2AssertMixin

from . import factories
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
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        form = self.form(data={}, user=user, discussion=discussion)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_initial_subscribe(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        form = self.form(user=user, discussion=discussion)
        self.assertTrue(form.initial['subscribe'])

    def test_initial_unsubscribe(self):
        discussion = factories.DiscussionFactory.create()
        user = discussion.creator
        discussion.subscribers.add(user)
        form = self.form(user=user, discussion=discussion)
        self.assertFalse(form.initial['subscribe'])
