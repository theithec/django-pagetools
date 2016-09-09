# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-26 15:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widgets', '0002_auto_20160912_2314'),
    ]

    operations = [
        migrations.RenameField(
            model_name='typearea',
            old_name='type',
            new_name='pagetype',
        ),
        migrations.AlterUniqueTogether(
            name='typearea',
            unique_together=set([('area', 'pagetype', 'lang')]),
        ),
    ]
