import json

from django.conf import settings
from django.shortcuts import render

from lexicon.forms import formset_for_lg
from mesolex.config import LANGUAGES
from mesolex.utils import ForceProxyEncoder, get_default_data_for_lg
from narratives.forms import SoundMetadataQueryComposerFormset


def home(request, *args, **kwargs):
    template_name = 'home.html'
    return render(request, template_name, {
        'languages': json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
        'lexicon': {
            'formset': formset_for_lg(None),
            'formset_data': json.dumps(get_default_data_for_lg(None)),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
        'narratives': {
            'formset': SoundMetadataQueryComposerFormset(),
            'formset_data': json.dumps(get_default_data_for_lg(LANGUAGES['narratives'])),
            'formset_global_filters_form_data': json.dumps({}),
            'formset_datasets_form_data': json.dumps({}),
            'formset_errors': json.dumps([]),
            'form_captions': True,
        },
    })
