# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0010_create_comment_base_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextComment',
            fields=[
                ('basecomment_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='groups.BaseComment', parent_link=True)),
                ('body', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('groups.basecomment',),
        ),
    ]
