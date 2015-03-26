# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_alter_related_names'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='discussion',
            options={'ordering': ['-date_created']},
        ),
    ]
