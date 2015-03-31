# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0007_change_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='state',
            field=models.CharField(max_length=255, default='ok', choices=[('ok', 'OK'), ('deleted', 'Deleted')]),
            preserve_default=True,
        ),
    ]
