from django import forms
from django.db.models import Q

from mesolex.config import DATASETS
from query_builder.forms import QueryBuilderGlobalFiltersForm


class LexiconQueryBuilderGlobalFiltersForm(QueryBuilderGlobalFiltersForm):
    only_with_sound = forms.BooleanField(required=False)
    dataset = forms.ChoiceField(
        choices=[(l['code'], l['label']) for l in DATASETS.values()],
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def clean_only_with_sound(self):
        only_with_sound = self.cleaned_data['only_with_sound']
        if only_with_sound:
            return Q(media__isnull=(not only_with_sound))

        return False

    def clean_dataset(self):
        dataset = self.cleaned_data['dataset']
        if dataset:
            return Q(dataset=dataset)

        return False
