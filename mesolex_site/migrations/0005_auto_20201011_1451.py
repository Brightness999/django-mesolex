# Generated by Django 3.0.7 on 2020-10-11 14:51

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('mesolex_site', '0004_searchpage_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='languagehomepage',
            name='corpora',
        ),
        migrations.RemoveField(
            model_name='languagehomepage',
            name='grammar',
        ),
        migrations.RemoveField(
            model_name='languagehomepage',
            name='lexicons',
        ),
        migrations.AddField(
            model_name='languagehomepage',
            name='corpus_resources',
            field=wagtail.core.fields.StreamField([('corpus_resource_link', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('resource_page', wagtail.core.blocks.PageChooserBlock(page_type=['mesolex_site.LanguageResourcePage', 'mesolex_site.SearchPage'], required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))], blank=True),
        ),
        migrations.AddField(
            model_name='languagehomepage',
            name='grammatical_resources',
            field=wagtail.core.fields.StreamField([('grammatical_resource_link', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('resource_page', wagtail.core.blocks.PageChooserBlock(page_type=['mesolex_site.LanguageResourcePage', 'mesolex_site.SearchPage'], required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))], blank=True),
        ),
        migrations.AddField(
            model_name='languagehomepage',
            name='lexical_resources',
            field=wagtail.core.fields.StreamField([('lexical_resource_link', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('resource_page', wagtail.core.blocks.PageChooserBlock(page_type=['mesolex_site.LanguageResourcePage', 'mesolex_site.SearchPage'], required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))], blank=True),
        ),
    ]
