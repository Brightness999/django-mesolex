# Generated by Django 3.2.7 on 2021-10-10 16:54

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(db_index=True, max_length=256, unique=True)),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('dataset', models.CharField(max_length=64)),
                ('data', models.JSONField(blank=True, null=True)),
                ('parent_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lexicon.entry')),
            ],
            options={
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.CreateModel(
            name='SearchableString',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=64)),
                ('type_tag', models.CharField(db_index=True, max_length=256)),
                ('other_data', models.JSONField(blank=True, null=True)),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.entry')),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('mime_type', models.CharField(default='audio/mpeg', max_length=64)),
                ('lexical_entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lexicon.entry')),
            ],
            options={
                'verbose_name': 'Media File Link',
            },
        ),
        migrations.CreateModel(
            name='LongSearchableString',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=64)),
                ('type_tag', models.CharField(db_index=True, max_length=256)),
                ('other_data', models.JSONField(blank=True, null=True)),
                ('value', models.TextField()),
                ('searchable_value', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.entry')),
            ],
        ),
        migrations.AddIndex(
            model_name='searchablestring',
            index=django.contrib.postgres.indexes.GinIndex(fields=['value'], name='ss_value_gin_idx', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='searchablestring',
            index=django.contrib.postgres.indexes.GinIndex(fields=['type_tag'], name='ss_type_tag_gin_idx', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='longsearchablestring',
            index=django.contrib.postgres.indexes.GinIndex(fields=['searchable_value'], name='lss_searchable_value_gin_idx'),
        ),
    ]
