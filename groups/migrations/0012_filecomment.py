# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0011_textcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileComment',
            fields=[
                ('basecomment_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, to='groups.BaseComment', primary_key=True)),
                ('file', models.FileField(upload_to='')),
            ],
            options={
                'abstract': False,
            },
            bases=('groups.basecomment',),
        ),
    ]
