# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-12 23:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0002_auto_20160907_1609'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagenodepos',
            options={'ordering': ['position'], 'verbose_name': 'Included Content', 'verbose_name_plural': 'Included Content'},
        ),
    ]
