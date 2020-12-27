# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-07 16:09
from __future__ import unicode_literals
import django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sections", "0001_initial"),
    ]
    operations = []
    if django.VERSION >= (1, 9):
        Operations = [
            migrations.AlterField(
                model_name="pagenode",
                name="slug",
                field=models.SlugField(
                    allow_unicode=True, max_length=255, verbose_name="Slug"
                ),
            ),
        ]
