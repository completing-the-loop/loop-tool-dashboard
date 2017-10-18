# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-13 03:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('olap', '0017_page_is_forum'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pagevisit',
            unique_together=set([('lms_user', 'page', 'visited_at')]),
        ),
        migrations.AlterUniqueTogether(
            name='submissionattempt',
            unique_together=set([('lms_user', 'page', 'attempted_at')]),
        ),
        migrations.AlterUniqueTogether(
            name='summarypost',
            unique_together=set([('lms_user', 'page', 'posted_at')]),
        ),
    ]