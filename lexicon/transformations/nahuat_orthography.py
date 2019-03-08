import re


OTHER = [
    '\(', '\)',
]

VOWELS = [
    'a', 'e', 'i', 'o', 'u',
    'á', 'é', 'í', 'ó', 'ú',
    'à', 'è', 'ì', 'ò', 'ù',
]

CONSONANTS = [
    'h',
    'kw', 'w',
    'k',
    'ch', 'x', 'y',
    'tl', 'l',
    'n', 't', 'ts', 's',
    'm', 'p',
    '$',
    '^',
]

EQUIVALENCE_SETS = [
    ["ka", "ca"],
    ["ko", "co"],
    ["ke", "que"],
    ["ki", "qui"],
    ["ku", "cu", "que"],
    ["ts", "tz"],
    # ["se", "ce"],
    # ["si", "ci"],
    ["sa", "za", "ça"],
    ["so", "zo", "ço"],
    ["kwe", "cue"],
    ["kwi", "cui"],
    ["kwa", "qua", "cua"],
]

# Unfortunately, we have to assume that all left
# contexts are *negative* lookbehind; otherwise we
# encounter nasty length-related issues.
CONTEXTUAL_EQUIVALENCE_SETS = [
    (
        set(['t']),
        ['se', 'ce'],
        [],
    ),
    (
        set(['t']),
        ['si', 'ci'],
        [],
    ),
    (
        set(['k', 'c', 'q']),
        ["w", "v", "hu", "u"],
        VOWELS,
    ),
    (
        set(['k', 'c', 'q']),
        ["w", "v", "uh", "u"],
        CONSONANTS
    ),
]


def transform_equivalences(query_string, equivalences):
    substitution_class = '({composed})'.format(
        composed='|'.join(equivalences)
    )
    return re.sub(re.compile(substitution_class), substitution_class, query_string)


def transform_equivalences_with_context(query_string, equivalences_with_contexts):
    equi_classes = '|'.join(equivalences_with_contexts[1])
    lookbehind_classes = '|'.join(equivalences_with_contexts[0])
    lookahead_classes = '|'.join(equivalences_with_contexts[2])
    substitution_class = '(?<!{lookbehind})({equi})(?=({lookahead}))'.format(
        lookbehind=lookbehind_classes,
        equi=equi_classes,
        lookahead=lookahead_classes,
    )
    target_transformation = '({equi})'.format(equi=equi_classes)
    return re.sub(re.compile(substitution_class), target_transformation, query_string)

def _transform(query_string):
    new_string = query_string

    for equivalences in EQUIVALENCE_SETS:
        new_string = transform_equivalences(new_string, equivalences)
    
    for equivalences in CONTEXTUAL_EQUIVALENCE_SETS:
        new_string = transform_equivalences_with_context(new_string, equivalences)

    return new_string


def transform(filter_name, filter_action, query_string, form_data):
    if not form_data['neutralize_orthography']:
        return (filter_action, query_string)
    
    return ('__iregex', _transform(query_string))
    
