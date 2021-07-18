from .azz import AzzLexicalSearchFilterFormset as AzzFormset
from .juxt1235_verb import Juxt1235VerbLexicalSearchFilterFormset as Juxt1235VerbFormset
from .juxt1235_non_verb import Juxt1235NonVerbLexicalSearchFilterFormset as Juxt1235NonVerbFormset
from .trq import TrqLexicalSearchFilterFormset as TrqFormset
from .plantnames_oax import PnoLexicalSearchFilterFormset as PnoFormset

DEFAULT_FORMSET = AzzFormset


def formset_for_dataset(dataset_code):
    if dataset_code == 'azz':
        return AzzFormset
    if dataset_code == 'trq':
        return TrqFormset
    if dataset_code == 'juxt1235_verb':
        return Juxt1235VerbFormset
    if dataset_code == 'juxt1235_non_verb':
        return Juxt1235NonVerbFormset
    if dataset_code == 'plantnames_oax':
        return PnoFormset

    return DEFAULT_FORMSET
