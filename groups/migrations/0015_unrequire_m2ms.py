# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0014_discussion_ignorers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='ignorers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='ignored_discussions'),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='subscribers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='subscribed_discussions'),
        ),
        migrations.AlterField(
            model_name='group',
            name='members_if_private',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='private_groups_joined'),
        ),
        migrations.AlterField(
            model_name='group',
            name='moderators',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='moderated_groups'),
        ),
        migrations.AlterField(
            model_name='group',
            name='watchers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='watched_groups'),
        ),
    ]
