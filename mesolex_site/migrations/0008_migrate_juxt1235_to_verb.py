# Generated by Django 3.0.7 on 2021-03-21 14:33

from django.db import migrations


def update_dataset_code_value(apps, _schema_editor):
    SearchPage = apps.get_model('mesolex_site', 'SearchPage')
    SearchPage.objects.filter(dataset_code='juxt1235').update(dataset_code='juxt1235_verb')


def revert_dataset_code_value_change(apps, schema_editor):
    SearchPage = apps.get_model('mesolex_site', 'SearchPage')
    SearchPage.objects.filter(dataset_code='juxt1235_verb').update(dataset_code='juxt1235')


class Migration(migrations.Migration):

    dependencies = [
        ('mesolex_site', '0007_auto_20210321_1419'),
    ]

    operations = [
        migrations.RunPython(
            update_dataset_code_value,
            revert_dataset_code_value_change,
        ),
    ]
