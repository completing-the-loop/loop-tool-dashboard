# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-02 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_courseoffering_lms_server'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseoffering',
            name='code',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='courseoffering',
            unique_together=set([('code', 'lms_server')]),
        ),
    ]