# Generated by Django 4.2.3 on 2023-11-27 20:43

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0008_auto_20170301_2044"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="content",
            field=tinymce.models.HTMLField(verbose_name="Content"),
        ),
    ]
