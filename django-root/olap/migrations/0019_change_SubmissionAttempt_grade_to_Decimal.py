# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-16 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olap', '0018_activity_uniqueness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissiontype',
            name='grade',
            field=models.DecimalField(decimal_places=4, max_digits=7),
        ),
    ]
