# Generated by Django 3.0.7 on 2021-04-04 14:12

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0022_auto_20210404_1247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='longsearchablestring',
            options={},
        ),
        migrations.AddField(
            model_name='longsearchablestring',
            name='searchable_value',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='longsearchablestring',
            index=django.contrib.postgres.indexes.GinIndex(fields=['searchable_value'], name='lss_searchable_value_gin_idx'),
        ),
    ]
