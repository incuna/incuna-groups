# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0015_unrequire_m2ms'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachedFileComment',
            fields=[
                ('filecomment_ptr', models.OneToOneField(serialize=False, to='groups.FileComment', primary_key=True, parent_link=True, auto_created=True)),
                ('attached_to', models.ForeignKey(blank=True, to='groups.BaseComment', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('groups.filecomment',),
        ),
    ]
