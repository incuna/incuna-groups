# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0009_comment_polymorphic_ctype'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseComment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('state', models.CharField(max_length=255, choices=[('ok', 'OK'), ('deleted', 'Deleted')], default='ok')),
                ('discussion', models.ForeignKey(to='groups.Discussion', related_name='comments')),
                ('polymorphic_ctype', models.ForeignKey(null=True, editable=False, to='contenttypes.ContentType', related_name='polymorphic_groups.basecomment_set')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='comments')),
            ],
            options={
                'ordering': ('date_created',),
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='comment',
            name='discussion',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
