# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_add_comment_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='comment',
            name='discussion',
            field=models.ForeignKey(to='groups.Discussion', related_name='comments'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='comments'),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='created_discussions'),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='group',
            field=models.ForeignKey(to='groups.Group', related_name='discussions'),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='subscribers',
            field=models.ManyToManyField(related_name='subscribed_discussions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='members_if_private',
            field=models.ManyToManyField(related_name='private_groups_joined', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='moderators',
            field=models.ManyToManyField(related_name='moderated_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='watchers',
            field=models.ManyToManyField(related_name='watched_groups', to=settings.AUTH_USER_MODEL),
        ),
    ]
