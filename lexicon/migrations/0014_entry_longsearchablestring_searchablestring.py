# Generated by Django 3.0.7 on 2020-11-15 16:05

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0013_lexicalentry_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=256, unique=True)),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('language', models.CharField(max_length=64)),
                ('other_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('parent_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lexicon.Entry')),
            ],
        ),
        migrations.CreateModel(
            name='SearchableString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=64)),
                ('type_tag', models.CharField(db_index=True, max_length=256)),
                ('other_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.Entry')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LongSearchableString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=64)),
                ('type_tag', models.CharField(db_index=True, max_length=256)),
                ('other_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('value', models.TextField()),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.Entry')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
