# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 06:23
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0017_remove_file_comment'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='textcomment',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]