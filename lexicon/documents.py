from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import LexicalEntry, Note, Quote, Sense


@registry.register_document
class LexicalEntryDocument(Document):
    class Index:
        name = 'lexical_entry'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = LexicalEntry
        fields = [
            'lemma',
        ]

    quotations_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )
    quotations_azz = fields.TextField(multi=True)

    definitions_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    ostentives_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    nsem_es = fields.TextField(
        analyzer='spanish',
        multi=True,
    )

    def prepare_definitions_es(self, instance):
        return list(
            Sense.objects.filter(entry__id=instance.id)
            .values_list('definition', flat=True)
        )

    def prepare_ostentives_es(self, instance):
        return list(
            Sense.objects.filter(entry__id=instance.id)
            .values_list('ostentive', flat=True)
        )

    def prepare_quotations_es(self, instance):
        return list(
            Quote.objects.filter(example__sense__entry__id=instance.id)
            .filter(language='es')
            .values_list('text', flat=True)
        )

    def prepare_quotations_azz(self, instance):
        return list(
                Quote.objects.filter(example__sense__entry__id=instance.id)
                .filter(language='azz')
                .values_list('text', flat=True)
            )

    def prepare_nsem_es(self, instance):
        return list(
            Note.objects.filter(entry__id=instance.id)
            .filter(type='semantics')
            .values_list('value', flat=True)
        )
