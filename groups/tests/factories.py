import factory
from django.contrib.auth import get_user_model
from incuna_test_utils.factories import images

from .. import models


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence('user{}'.format)
    first_name = factory.Sequence('Leeroy{}'.format)
    last_name = factory.Sequence('Jenkins{}'.format)
    email = factory.Sequence('email{}@example.com'.format)
    is_active = True

    class Meta:
        model = get_user_model()

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        # By using this method, password can never be set to `None`!
        self.raw_password = 'password' if extracted is None else extracted
        self.set_password(self.raw_password)
        if create:
            self.save()


class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True


class GroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence('Group {}'.format)

    class Meta:
        model = models.Group


class DiscussionFactory(factory.DjangoModelFactory):
    name = factory.Sequence('Discussion {}'.format)
    group = factory.SubFactory(GroupFactory)
    creator = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Discussion


class BaseCommentFactory(factory.DjangoModelFactory):
    discussion = factory.SubFactory(DiscussionFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.BaseComment


class TextCommentFactory(BaseCommentFactory):
    body = factory.Sequence('Comment {}'.format)

    class Meta:
        model = models.TextComment


class AttachedFileFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    file = images.LocalFileField()
    attached_to = None

    class Meta:
        model = models.AttachedFile
