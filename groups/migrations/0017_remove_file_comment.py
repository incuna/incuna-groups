# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0016_attachedfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filecomment',
            name='basecomment_ptr',
        ),
        migrations.DeleteModel(
            name='FileComment',
        ),
    ]
