# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0013_update_filecomment_upload_update_basecomment_related_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussion',
            name='ignorers',
            field=models.ManyToManyField(related_name='ignored_discussions', to=settings.AUTH_USER_MODEL),
        ),
    ]
