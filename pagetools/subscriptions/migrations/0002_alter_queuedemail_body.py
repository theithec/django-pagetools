# Generated by Django 4.2.16 on 2024-11-12 13:49

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="queuedemail",
            name="body",
            field=tinymce.models.HTMLField(blank=True, default="", verbose_name="Body"),
        ),
    ]