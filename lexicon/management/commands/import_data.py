import csv
import itertools
import logging
from collections import defaultdict
from typing import Tuple
import xml.etree.ElementTree as ET

from dateutil.parser import ParserError, parse
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Func, Value
from django.utils.translation import gettext as _

from lexicon import models

logger = logging.getLogger(__name__)


class Importer():
    # meaning of returned tuple:
    # (created, updated, total)
    def __call__(self) -> Tuple[int, int, int]:
        raise NotImplementedError()


class XmlImporter(Importer):
    def __init__(self, input_file):
        self.input = input_file

    def _handle_root(self, root):
        raise NotImplementedError()

    def __call__(self):
        tree = ET.parse(self.input)
        root = tree.getroot()
        return self._handle_root(root)


class CsvImporter(Importer):
    def __init__(self, input_file):
        self.input = input_file

    def process_row(self, row, i):
        raise NotImplementedError()

    def __call__(self):
        (total, created, updated, i) = (0, 0, 0, 0)

        with open(self.input) as input_file:
            reader = csv.DictReader(input_file)

            for row in reader:
                total += 1
                try:
                    created_entry = self.process_row(row, i)
                    if created_entry is None:
                        pass
                    elif not created_entry:
                        updated += 1
                    elif created_entry:
                        created += 1
                except Exception as err:
                    logger.error('Error (row %d): %s', i, err)
                finally:
                    i += 1

        return (created, updated, total)

class MixtecPlantNamesImporter(CsvImporter):
    DATASET = "yolo1241"

    columns = ["col_num", "family", "genus", "species", "after_genus", 
               "subspecies_etc", "author", "c1_village", 
               "nombre_1", "glosa_nombre_1", "nombre_2", "glosa_nombre_2", 
               "nombre_3", "glosa_nombre_3", "commentary", 
               "field_recording_uid", "field_recording_summary", 
               "genus_species"]

    searchable_fields = [
        "family", "genus", "nombre_1", "glosa_nombre_1", "nombre_2", 
        "glosa_nombre_2", "nombre_3", "glosa_nombre_3", "genus_species"
    ]

    count = 1

    def initialize_data(self, row):

        entry_data = {
            'language': 'yolo1241', 
            'meta': {}
        }

        identifier = self.count
        self.count += 1
        entry_data['meta']['id'] = identifier
        
        entry_data["language"] = self.DATASET
        for col, val in row.items():
            if col not in self.searchable_fields:
                entry_data[col] = row[col]

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier,
            dataset=self.DATASET
        )
        return (entry, entry_data, created)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, row, entry, entry_data):
        new_searchable_strings = []
        for col, value in row.items():
            if col not in self.searchable_fields:
                continue
            if not value:
                entry_data[col] = value
                continue

            type_tag = col

            if type_tag.startswith("nombre_"):
                general_type_tag = "nombre"
            elif type_tag.startswith("glosa_"):
                general_type_tag = "glosa"
            else:
                general_type_tag = type_tag

            new_searchable_strings.append(
                models.SearchableString(
                    entry=entry,
                    value=value,
                    language="yolo1241",
                    type_tag=general_type_tag,
                )
            )
            entry_data[type_tag] = value

        models.SearchableString.objects.bulk_create(new_searchable_strings)

    @transaction.atomic
    def process_row(self, row, i):
        (entry, entry_data, created) = self.initialize_data(row)
        self.clean_up_associated_data(entry)
        self.create_simple_string_data(row, entry, entry_data)

        entry.data = entry_data
        entry.save()

        return created


class AzzImporter(XmlImporter):
    def create_searchable_strings(
            self,
            lx_group,
            tag,
            model_class,
            type_tag,
            entry,
            other_data=None,
    ):
        elements = lx_group.findall(tag)
        values = [
            element.text for element in elements
        ]

        if other_data is None:
            other_data = {}

        model_class.objects.bulk_create([
            model_class(
                value=value,
                entry=entry,
                language='azz',
                type_tag=type_tag,
                other_data=other_data,
            ) for value in values
        ])

        return values

    def initialize_data(self, lx_group, i):
        entry_data = defaultdict(list)

        entry_data['meta'] = {}
        entry_data['roots'] = {}

        # Find and fetch / create entry
        identifier = lx_group.find('ref')
        if identifier is None:
            logger.error('No ref found for lxGroup at index %d', i)
            return (None, None, None)

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier.text,
        )
        entry.dataset = 'azz'
        entry_data['language'] = 'azz'

        return (entry, entry_data, created)

    def process_basic_data(self, lx_group, i, entry, entry_data):
        # Associate basic data and metadata
        date = lx_group.find('dt')
        try:
            if date is not None:
                parsed_date = parse(date.text)
                entry_data['meta']['date'] = parsed_date.isoformat()
        except ParserError:
            logger.error('Invalid date for lxGroup at index %d', i)

        lemma = lx_group.find('lx')
        if lemma is None:
            logger.error('No lx found for lxGroup at index %d', i)
            return (None, 'Not found')

        entry.value = lemma.text
        entry_data['headword'] = lemma.text
        return (entry, None)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, lx_group, entry, entry_data):
        entry_data['meta']['variant_data'] = self.create_searchable_strings(
            lx_group,
            'lx_var',
            models.SearchableString,
            'variant_data',
            entry,
        )

        entry_data['citation_forms'] = self.create_searchable_strings(
            lx_group,
            'lx_cita',
            models.SearchableString,
            'citation_form',
            entry,
        )

        for type_tag in ['variant_form', 'lemma']:
            entry_data['variant_forms'] = self.create_searchable_strings(
                lx_group,
                'lx_alt',
                models.SearchableString,
                type_tag,
                entry,
            )

        entry_data['categories'] = self.create_searchable_strings(
            lx_group,
            'sem',
            models.SearchableString,
            'category',
            entry,
        )

        entry_data['roots']['simple'] = self.create_searchable_strings(
            lx_group,
            'raiz',
            models.SearchableString,
            'root',
            entry,
            {
                'root_type': 'simple',
            },
        )
        entry_data['roots']['compound'] = self.create_searchable_strings(
            lx_group,
            'raiz2',
            models.SearchableString,
            'root',
            entry,
            {
                'root_type': 'compound',
            },
        )

        entry_data['glosses'] = self.create_searchable_strings(
            lx_group,
            'glosa',
            models.SearchableString,
            'gloss',
            entry,
        )

    def create_notes(self, lx_group, entry, entry_data):
        entry_data['notes'].extend([
            {
                'note_type': 'note',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nota',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'note',
                },
            )
        ])
        entry_data['notes'].extend([
            {
                'note_type': 'semantics',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nsem',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'semantics',
                },
            )
        ])
        entry_data['notes'].extend([
            {
                'note_type': 'morphology',
                'text': value,
            } for value in self.create_searchable_strings(
                lx_group,
                'nmorf',
                models.LongSearchableString,
                'note',
                entry,
                {
                    'note_type': 'morphology',
                },
            )
        ])

    def create_etymologies(self, lx_group, entry, entry_data):
        pres_tipo_groups = lx_group.findall('pres_tipoGroup')
        pres_tipo_values = [
            {
                'type': group.find('pres_tipo').text,
                'value': group.find('pres_el').text,
            } for group in pres_tipo_groups
            if (
                group.find('pres_tipo') is not None
                and group.find('pres_el') is not None
            )
        ]
        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['value'],
                entry=entry,
                language='azz',
                type_tag='non_native_etymology',
                other_data={
                    'type': value['type'],
                },
            ) for value in pres_tipo_values
        ])
        entry_data['non_native_etymologies'].extend(pres_tipo_values)

    def create_grammars(self, lx_group, entry, entry_data):
        catgr_groups = lx_group.findall('catgrGroup')
        catgr_values = []
        for catgr_group in catgr_groups:
            catgr_value = {'other_data': {}}

            catgr = catgr_group.find('catgr')
            if catgr is not None:
                catgr_value['part_of_speech'] = catgr.text

            infl_group = catgr_group.find('inflGroup')
            if infl_group is not None:
                infl = infl_group.find('infl')
                if infl is not None:
                    catgr_value['inflectional_type'] = infl.text

                plural = infl_group.find('plural')
                if plural is not None:
                    catgr_value['other_data']['plural'] = plural.text

            diag = catgr_group.find('diag')
            if diag is not None:
                catgr_value['other_data']['diag'] = diag.text

            catgr_values.append(catgr_value)

        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['part_of_speech'],
                entry=entry,
                language='azz',
                type_tag='part_of_speech',
            ) for value in catgr_values
            if value.get('part_of_speech') is not None
        ])
        models.SearchableString.objects.bulk_create([
            models.SearchableString(
                value=value['inflectional_type'],
                entry=entry,
                language='azz',
                type_tag='inflectional_type',
            ) for value in catgr_values
            if value.get('inflectional_type') is not None
        ])
        entry_data['grammar_groups'].extend(catgr_values)

    def create_definitions(self, lx_group, entry, entry_data):
        sig_groups = lx_group.findall('sigGroup')
        sig_values = []
        for sig_group in sig_groups:
            sig_value = {}

            sig = sig_group.find('sig')
            if sig is not None:
                sig_value['sense'] = sig.text

            sig_var = sig_group.find('sig_var')
            if sig_var is not None:
                sig_value['geo'] = sig_var.text

            ostens = sig_group.findall('osten')
            if ostens is not None:
                sig_value['ostentives'] = [
                    osten.text for osten in ostens
                ]

            examples = []
            fr_n_groups = sig_group.findall('fr_nGroup')
            for fr_n_group in fr_n_groups:
                example_value = {}

                fr_var = fr_n_group.find('fr_var')
                if fr_var is not None:
                    example_value['geo'] = fr_var.text

                fr_n = fr_n_group.find('fr_n')
                if fr_n is not None:
                    example_value['original'] = {
                        'text': fr_n.text,
                        'language': 'azz',
                    }

                fr_e = fr_n_group.find('fr_e')
                if fr_e is not None:
                    example_value['translation'] = {
                        'text': fr_e.text,
                        'language': 'es',
                    }

                examples.append(example_value)

            for type_tag in ['quote_translation', 'complete_search']:
                models.LongSearchableString.objects.bulk_create([
                    models.LongSearchableString(
                        value=example['translation']['text'],
                        entry=entry,
                        language='es',
                        type_tag=type_tag,
                    ) for example in examples
                    if example.get('translation') is not None
                ])

            sig_value['examples'] = examples
            sig_values.append(sig_value)

        for type_tag in ['sense', 'extended_meaning', 'complete_search']:
            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=sig_value.get('sense', ''),
                    entry=entry,
                    language='es',
                    type_tag=type_tag,
                    other_data={
                        'geo': sig_value.get('geo'),
                        'ostentives': sig_value.get('ostentives', []),
                    },
                ) for sig_value in sig_values
            ])

        for type_tag in ['ostentive', 'extended_meaning', 'complete_search']:
            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=osten_value,
                    entry=entry,
                    language='es',
                    type_tag=type_tag,
                ) for osten_value in list(itertools.chain(
                    *[sig_value.get('ostentives', []) for sig_value in sig_values],
                ))
            ])
        entry_data['senses'].extend(sig_values)

    @transaction.atomic
    def process_lx_group(self, lx_group, i):
        (entry, entry_data, created) = self.initialize_data(lx_group, i)
        if any([x is None for x in [entry, entry_data, created]]):
            return None

        # Associate basic data and metadata
        (_, err) = self.process_basic_data(lx_group, i, entry, entry_data)
        if err is not None:
            return err

        # Clean up previously associated search data.
        self.clean_up_associated_data(entry)

        models.SearchableString.objects.create(
            value=entry_data['headword'],
            entry=entry,
            language='azz',
            type_tag='lemma',
        )

        for method in [
                self.create_simple_string_data,
                self.create_notes,
                self.create_etymologies,
                self.create_grammars,
                self.create_definitions,
        ]:
            method(lx_group, entry, entry_data)

        # Save the result
        entry.data = entry_data
        entry.save()

        return created

    def _handle_root(self, root):
        lx_groups = root.findall('lxGroup')
        created = 0
        updated = 0

        for i, lx_group in enumerate(lx_groups):
            try:
                created_entry = self.process_lx_group(lx_group, i)
                if created_entry is None:
                    pass
                elif not created_entry:
                    updated += 1
                elif created_entry:
                    created += 1
            except Exception as err:
                logger.error('Error: %s', err)
                continue

        return (created, updated, len(lx_groups))


class TrqImporter(XmlImporter):
    def create_searchable_strings(
            self,
            entry_el,
            xpath,
            model_class,
            type_tag,
            entry,
            other_data=None,
    ):
        elements = entry_el.findall(xpath)
        values = [element.text for element in elements]

        if other_data is None:
            other_data = {}

        model_class.objects.bulk_create([
            model_class(
                value=value,
                entry=entry,
                language='trq',
                type_tag=type_tag,
                other_data=other_data,
            ) for value in values
        ])

        return values

    def initialize_data(self, entry_el, i):
        entry_data = defaultdict(list)
        entry_data['meta'] = {}

        identifier = entry_el.attrib.get('guid')
        if identifier is None:
            logger.error('No guid found for entry at index %d', i)
            return (None, None, None)

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier,
        )
        entry.dataset = 'trq'
        entry_data['language'] = 'trq'

        return (entry, entry_data, created)

    def process_basic_data(self, entry_el, entry, entry_data):
        try:
            entry_data['meta']['date'] = parse(
                entry_el.attrib.get('dateModified')
                or entry_el.attrib.get('dateCreated')
            ).isoformat()
        except Exception:
            logger.exception(
                'Failed to parse date in entry with id %s',
                entry.identifier,
            )

        try:
            headword = entry_el.find(
                './lexical-unit/form[@lang="trq"]/text',
            ).text
            entry.value = headword
            entry_data['headword'] = headword
        except Exception:
            logger.exception(
                'Failed to find headword in entry with id %s',
                entry.identifier,
            )
            return (None, 'Not found')

        return (entry, None)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, entry_el, entry, entry_data):
        entry_data['citation_forms'] = self.create_searchable_strings(
            entry_el,
            './citation/form/text',
            models.SearchableString,
            'citation_form',
            entry,
        )

    def create_definitions(self, entry_el, entry, entry_data):
        senses = entry_el.findall('./sense')
        senses.sort(key=lambda sense: sense.attrib.get('order', 0))

        # data to return
        sense_values = []

        for sense_element in senses:
            sense_value = {}

            # NOTE: disjunction on etree elements isn't short-circuiting!
            # TODO: find a properly short-circuiting method to go here
            # to prevent some unnecessary queries
            definition_element = (
                sense_element.find('./gloss/text')
                or sense_element.find('./definition/form/text')
            )

            if definition_element is not None:
                sense_value['sense'] = definition_element.text
            else:
                continue

            examples = []
            example_els = sense_element.findall('example')
            for example_el in example_els:
                example_value = {}

                ex_text = example_el.find('./form[@lang="es-MX-fonipa-x-emic"]/text/span')
                if ex_text is not None:
                    example_value['original'] = {
                        'text': ex_text.text,
                        'language': 'trq',
                    }

                ex_translation = example_el.find('./translation/form[@lang="es"]/text')
                if ex_translation is not None:
                    example_value['translation'] = {
                        'text': ex_translation.text,
                        'language': 'es',
                    }

                examples.append(example_value)

            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['original']['text'],
                    entry=entry,
                    language='trq',
                    type_tag='quote_original',
                ) for example in examples
                if example.get('original') is not None
            ])
            models.LongSearchableString.objects.bulk_create([
                models.LongSearchableString(
                    value=example['translation']['text'],
                    entry=entry,
                    language='es',
                    type_tag='quote_translation',
                ) for example in examples
                if example.get('translation') is not None
            ])

            sense_value['examples'] = examples
            sense_values.append(sense_value)

        models.LongSearchableString.objects.bulk_create([
            models.LongSearchableString(
                value=sense_value.get('sense', ''),
                entry=entry,
                language='es',
                type_tag='sense',
                other_data={},
            ) for sense_value in sense_values
        ])
        entry_data['senses'].extend(sense_values)

    @transaction.atomic
    def process_entry(self, entry_el, i):
        (entry, entry_data, created) = self.initialize_data(entry_el, i)
        if any([x is None for x in [entry, entry_data, created]]):
            return None

        (_, err) = self.process_basic_data(entry_el, entry, entry_data)
        if err is not None:
            return err

        self.clean_up_associated_data(entry)

        models.SearchableString.objects.create(
            value=entry_data['headword'],
            entry=entry,
            language='trq',
            type_tag='lemma',
        )

        for method in [
                self.create_simple_string_data,
                self.create_definitions,
        ]:
            method(entry_el, entry, entry_data)

        entry.data = entry_data
        entry.save()

        return created

    def _handle_root(self, root):
        entries = root.findall('entry')
        created = 0
        updated = 0

        for i, entry_el in enumerate(entries):
            try:
                created_entry = self.process_entry(entry_el, i)
                if created_entry is None:
                    pass
                elif not created_entry:
                    updated += 1
                elif created_entry:
                    created += 1
            except Exception as err:
                logger.error('Error: %s', err)
                continue

        return (created, updated, len(entries))


class Juxt1235VerbImporter(CsvImporter):
    HEADER_TO_FIELD_NAME = {
        'IRR_TL': 'irr_tl',
        'IMPF': 'impf',
        'PFV': 'pfv',
        'IRR': ['irr', 'headword'],
        'Valence': 'valence',
        'Class verbal': 'class_verbal',
        'Spanish': 'spanish',
        'English': 'english',
        'Morphemes': 'morphemes',
        'GlossEnglish': 'gloss_english',
        'GlossSpanish': 'gloss_spanish',
        'IMPF_TONE_MEL (SP)': 'impf_tone_mel_sp',
        'PFV_TONE_MEL (SP)': 'pfv_tone_mel_sp',
        'IRR_TONE_MEL (SP)': 'irr_tone_mel_sp',
        'IMPF_TONE_MEL (ENG)': 'impf_tone_mel_en',
        'PFV_TONE_MEL (ENG)': 'pfv_tone_mel_en',
        'IRR_TONE_MEL (ENG)': 'irr_tone_mel_en',
        'NEG.IMPF': 'neg_impf',
        'NEG.PFV': 'neg_pfv',
        'NEG.IRR1': 'neg_irr_1',
        'NEG.IRR2': 'neg_irr_2',
        'pMx': 'p_mx',
        'Source': 'source',
        'Note': 'notes',
    }
    NORMALIZED_FIELDS = [
        'headword',
        'impf',
        'pfv',
        'irr',
        'neg_impf',
        'neg_pfv',
        'neg_irr_1',
        'neg_irr_2',
        'p_mx',
    ]
    SPECIAL_NORMALIZED_FIELDS = {
        'neg_irr_1': 'neg_irr_normalized',
        'neg_irr_2': 'neg_irr_normalized',
    }

    def initialize_data(self, row):
        entry_data = {'language': 'juxt1235', 'meta': {}}
        identifier = row['ID']
        entry_data['meta']['id'] = identifier

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier,
            dataset='juxt1235_verb',
        )

        entry.value = row['IRR']

        return (entry, entry_data, created)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, row, entry, entry_data):
        new_searchable_strings = []

        for item_key, item_value in row.items():
            field_names = self.HEADER_TO_FIELD_NAME.get(item_key)
            if field_names is None:
                continue
            if not isinstance(field_names, list):
                field_names = [field_names]

            for field_name in field_names:
                if item_value != '':
                    new_searchable_strings.append(models.SearchableString(
                        entry=entry,
                        value=item_value,
                        language='juxt1235',
                        type_tag=field_name,
                    ))
                    if field_name in self.NORMALIZED_FIELDS:
                        new_searchable_strings.append(models.SearchableString(
                        entry=entry,
                        value=item_value,
                        language='juxt1235',
                        type_tag=self.SPECIAL_NORMALIZED_FIELDS.get('field_name') or f'{field_name}_normalized',
                    ))
                        new_searchable_strings.append(models.SearchableString(
                            entry=entry,
                            value=Func(Value(item_value), function='unaccent'),
                            language='juxt1235',
                            type_tag=self.SPECIAL_NORMALIZED_FIELDS.get('field_name') or f'{field_name}_normalized',
                        ))

                entry_data[field_name] = item_value

        models.SearchableString.objects.bulk_create(new_searchable_strings)

    @transaction.atomic
    def process_row(self, row, i):
        (entry, entry_data, created) = self.initialize_data(row)

        self.clean_up_associated_data(entry)

        self.create_simple_string_data(row, entry, entry_data)

        entry.data = entry_data
        entry.save()

        return created


class Juxt1235NonVerbImporter(CsvImporter):
    HEADER_TO_FIELD_NAME = {
        'Loan': 'loan',
        'Mixteco': ['mixteco', 'headword'],
        'MixtecoToneless': 'mixteco_toneless',
        'Spanish': 'spanish',
        'English': 'english',
        'WordClass': 'word_class_en',
        'ClasePalabra': 'word_class_es',
        'Pronoun': 'pronoun',
        'Morphemes': 'morphemes',
        'GlossEnglish': 'gloss_english',
        'GlossSpanish': 'gloss_spanish',
        'SemanticField': 'semantic_field_en',
        'CampoSemántico': 'semantic_field_es',
        'ScientificName': 'scientific_name',
        'Author etc': 'author',
        'Tone-Melody': 'tone_melody_en',
        'Tono-Melodia': 'tone_melody_es',
        'LToneChange': 'l_tone_change',
        'pMX': 'p_mx',
        'Source': 'source',
        'NotesForm': 'notes_form',
        'NotesCulture': 'notes_culture',
        'NotesMeta': 'notes_meta',
    }
    NORMALIZED_FIELDS = [
        'headword',
        'mixteco',
        'p_mx',
    ]
    LONG_FIELDS = [
        'l_tone_change',
        'notes_form',
        'notes_culture',
        'notes_meta',
    ]

    def initialize_data(self, row):
        entry_data = {'language': 'juxt1235', 'meta': {}}
        identifier = row['ID']
        entry_data['meta']['id'] = identifier

        entry, created = models.Entry.objects.get_or_create(
            identifier=identifier,
            dataset='juxt1235_non_verb',
        )

        entry.value = row['Mixteco']

        return (entry, entry_data, created)

    def clean_up_associated_data(self, entry):
        entry.searchablestring_set.all().delete()
        entry.longsearchablestring_set.all().delete()

    def create_simple_string_data(self, row, entry, entry_data):
        new_searchable_strings = []
        new_long_searchable_strings = []

        for item_key, item_value in row.items():
            field_names = self.HEADER_TO_FIELD_NAME.get(item_key)
            if field_names is None:
                continue
            if not isinstance(field_names, list):
                field_names = [field_names]

            for field_name in field_names:
                if field_name in self.LONG_FIELDS:
                    searchable_string_class = models.LongSearchableString
                    searchable_string_bucket = new_long_searchable_strings
                else:
                    searchable_string_class = models.SearchableString
                    searchable_string_bucket = new_searchable_strings

                if item_value != '':
                    searchable_string_bucket.append(searchable_string_class(
                        entry=entry,
                        value=item_value,
                        language='juxt1235',
                        type_tag=field_name,
                    ))
                    if field_name in self.NORMALIZED_FIELDS:
                        searchable_string_bucket.append(searchable_string_class(
                            entry=entry,
                            value=Func(Value(item_value), function='unaccent'),
                            language='juxt1235',
                            type_tag=f'{field_name}_normalized',
                        ))

                entry_data[field_name] = item_value

        models.SearchableString.objects.bulk_create(new_searchable_strings)
        models.LongSearchableString.objects.bulk_create(new_long_searchable_strings)

    @transaction.atomic
    def process_row(self, row, i):
        (entry, entry_data, created) = self.initialize_data(row)

        self.clean_up_associated_data(entry)

        self.create_simple_string_data(row, entry, entry_data)

        entry.data = entry_data
        entry.save()

        return created


class Command(BaseCommand):
    help = _("Lee una fuente de datos en XML y actualiza la base de datos.")

    IMPORTERS_BY_CODE = {
        'azz': AzzImporter,
        'trq': TrqImporter,
        'yolo1241': MixtecPlantNamesImporter,
        'juxt1235_verb': Juxt1235VerbImporter,
        'juxt1235_non_verb': Juxt1235NonVerbImporter,
    }

    def add_arguments(self, parser):
        parser.add_argument('dataset', type=str)
        parser.add_argument('input', type=str)

    def handle(self, *args, **options):
        input_file = options['input']
        dataset = options['dataset']

        importer = self._importer_for(dataset, input_file)

        (added_entries, updated_entries, total) = (
            importer()
            if importer is not None
            else (0, 0, 0)
        )

        self.stdout.write('\n\nTOTAL: {add} added, {up} updated, {miss} missed'.format(
            add=added_entries,
            up=updated_entries,
            miss=(total - added_entries - updated_entries),
        ))

    def _importer_for(self, dataset, input_file):
        importer_class = self.IMPORTERS_BY_CODE.get(dataset, None)

        if importer_class is None:
            raise ValueError(f'Importer for dataset code {dataset} not found')

        return importer_class(input_file)
