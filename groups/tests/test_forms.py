from incuna_test_utils.compat import Python2AssertMixin
from incuna_test_utils.factories.images import uploadable_file

from . import factories
from .utils import RequestTestCase
from .. import forms, models


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


class TestAddFileComment(Python2AssertMixin, RequestTestCase):
    form = forms.AddFileComment
    model = models.FileComment

    def test_form_fields(self):
        expected = ['file']
        fields = self.form.base_fields.keys()
        self.assertCountEqual(fields, expected)

    def test_form_valid(self):
        file_data = {'file': uploadable_file()}

        form = self.form(files=file_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_not_valid(self):
        form = self.form(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)


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
