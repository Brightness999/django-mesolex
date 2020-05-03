/* global gettext */
import _ from 'lodash';

/*
  Returns a predicate to determine whether a value corresponds
  to a controlled vocabulary item for `filter_on`.
*/
export const controlledVocabCheck = (controlledVocabFields) => {
  const keys = _.keys(controlledVocabFields);
  return (value) => _.includes(keys, value);
};


/*
  Helper to render the text displayed above the input row.

  NOTE: it is not at all satisfactory to have vln and nahuatOrthography in here,
  as those propertly belong to the Lexicon app. TODO: move them over there and
  refactor to make that possible.
*/
export const humanReadableFilters = ({
  i,
  operator,
  filterOn,
  filter,
  vln,
  nahuatOrthography,
  filterableFields,
}) => {
  const initOpDict = {
    and: '',
    and_n: `${gettext('no')}:`,
    or: '',
    or_n: `${gettext('no')}:`,
  };
  const opDict = {
    and: `${gettext('y')}:`,
    or: `${gettext('o')}:`,
    and_n: `${gettext('y no')}:`,
    or_n: `${gettext('o no')}:`,
  };
  const filterDict = {
    begins_with: `${gettext('empieza con')}`,
    ends_with: `${gettext('termina con')}`,
    contains: `${gettext('contiene secuencia')}`,
    contains_word: `${gettext('contiene palabra')}`,
    exactly_equals: `${gettext('es exactamente igual a')}`,
    regex: `${gettext('coincide con expresión regular')}`,
    text_search: `${gettext('coincide con')}`,
  };
  const filterableFieldsDict = _.fromPairs(filterableFields);
  const modifiers = _.reduce(
    [
      [vln, gettext('NCV')],
      [nahuatOrthography, gettext('flex. ort.')],
    ],
    (acc, [val, repr]) => (val ? acc.concat(repr) : acc),
    [],
  );
  return `${i === 0 ? initOpDict[operator] : opDict[operator]} ${filterableFieldsDict[filterOn] || gettext('ítem')} ${filterDict[filter]}${modifiers.length ? ` (${modifiers.join(', ')})` : ''}`;
};

/**
 * Converts the structure of the LANGUAGES config's controlled
 * vocab fields to the {fieldName: [[value, label]]} structure
 * expected by the front-end.
 */
export const makeControlledVocabFields = (languagesCVFs) => _.chain(languagesCVFs)
  .map(({ field, items }) => ({ [field]: items }))
  .reduce((acc, next) => ({ ...acc, ...next }))
  .mapValues((items) => _.map(items, ({ value, label }) => [value, label]))
  .value();

export const makeFilterableFields = (...languageFFs) => _.map(
  _.concat(...languageFFs),
  ({ field, label }) => [field, label],
);
