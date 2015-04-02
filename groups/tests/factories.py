from io import BytesIO

import factory
from django.contrib.auth import get_user_model
from PIL import Image

from .. import models


TEST_SERVER = 'http://testserver'


def simple_png():
    """Create a 1x1 black png in memory."""
    image_file = BytesIO()
    image = Image.new('RGBA', (1, 1))
    image.save(image_file, 'png')
    image_file.name = 'test.png'
    image_file.url = '{0}/{1}'.format(
        TEST_SERVER,
        image_file.name,
    )
    image_file._committed = True
    image_file.seek(0)
    return image_file


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence('user{}'.format)
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


class TextCommentFactory(factory.DjangoModelFactory):
    body = factory.Sequence('Comment {}'.format)
    discussion = factory.SubFactory(DiscussionFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.TextComment


class FileCommentFactory(factory.DjangoModelFactory):
    file = factory.django.FileField(from_path='groups/tests/images/image.png')
    discussion = factory.SubFactory(DiscussionFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.FileComment
