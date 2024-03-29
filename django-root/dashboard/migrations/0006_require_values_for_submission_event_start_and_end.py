# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-11 04:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_require_values_for_start_and_end_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesubmissionevent',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursesubmissionevent',
            name='event_type',
            field=models.CharField(choices=[('assignment', 'Assignment'), ('quiz', 'Quiz')], default='assignment', max_length=50),
        ),
        migrations.AlterField(
            model_name='coursesubmissionevent',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
