# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-04 11:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0014_quote_translation_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='translation_of',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='lexicon.Quote'),
        ),
    ]