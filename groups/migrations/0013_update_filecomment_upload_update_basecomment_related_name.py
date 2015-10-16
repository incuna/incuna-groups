# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0012_filecomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecomment',
            name='polymorphic_ctype',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True, related_name='polymorphic_groups.basecomment_set+', editable=False),
        ),
        migrations.AlterField(
            model_name='filecomment',
            name='file',
            field=models.FileField(upload_to='groups/file_comments'),
        ),
    ]
