# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-27 12:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0004_auto_20160918_2055"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="page",
            unique_together=set([("slug", "lang")]),
        ),
    ]
