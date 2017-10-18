# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-11 05:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('olap', '0013_clean_up_SummaryPost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summarypost',
            name='page_id',
        ),
        migrations.AddField(
            model_name='summarypost',
            name='page',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='olap.Page'),
            preserve_default=False,
        ),
    ]