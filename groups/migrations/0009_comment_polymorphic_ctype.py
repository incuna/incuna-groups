# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('groups', '0008_comment_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='polymorphic_ctype',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True, related_name='polymorphic_groups.comment_set', editable=False),
            preserve_default=True,
        ),
    ]
