# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0015_unrequire_m2ms'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachedFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('file', models.FileField(upload_to='groups/attachments')),
                ('attached_to', models.ForeignKey(to='groups.BaseComment', null=True, blank=True, related_name='attachments')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='attachments')),
            ],
        ),
    ]
