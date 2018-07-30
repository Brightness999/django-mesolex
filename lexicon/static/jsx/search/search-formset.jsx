/* global gettext */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import uuid4 from 'uuid/v4';

import SearchForm from './search-form';


export default class SearchFormSet extends React.Component {
  static propTypes = {
    formsetData: PropTypes.shape.isRequired,
    formsetErrors: PropTypes.shape.isRequired,
  }

  /*
    Upon being initialized with formsetData and formsetErrors
    (which are provided from the rendered template on the basis
    of previously-submitted form data), the constructor will
    build an initial state consisting of:

    - `forms`, a simple list of unique identifiers
    - `formsetIndexedDatasets`, the form data for each form,
      indexed by the unique identifier from `forms`
    - `formsetIndexedErrors`, the errors for each form,
      indexed by the unique identifier from `forms`

    After being consumed, `formsetData` and `formsetErrors` are not used.
  */
  constructor(props) {
    super(props);
    const { formsetData, formsetErrors } = props;

    /*
      Construct the list of forms by invoking `uuid` n times,
      where n == the initial formset's count or 1.
    */
    const forms = _.times(
      parseInt(formsetData['form-TOTAL_FORMS'], 10) || 1,
      () => uuid4(),
    );

    /*
      Construct a single-key object with the `form` uuid
      as the key, then roll them all up together into one
      big object.
    */
    const formsetIndexedDatasets = _.reduce(
      _.map(
        forms,
        (uniqueId, i) => ({
          [uniqueId]: {
            query_string: formsetData[`form-${i}-query_string`] || '',
            operator: formsetData[`form-${i}-operator`] || 'and',
            filter_on: formsetData[`form-${i}-filter_on`] || 'headword',
            filter: formsetData[`form-${i}-filter`] || 'begins_with',
            vln: !!formsetData[`form-${i}-vln`],
          },
        }),
      ),
      (acc, dataset) => ({ ...acc, ...dataset }),
      {},
    );

    /*
      Construct the set of form errors by the same summing-up
      process as with formsetIndexedDatasets but with simpler
      construction logic (less postprocessing needed).
    */
    const formsetIndexedErrors = _.reduce(
      forms,
      (acc, uniqueId, i) => ({
        ...acc,
        [uniqueId]: formsetErrors[i] || {},
      }),
      {},
    );

    this.state = {
      forms,
      formsetIndexedDatasets,
      formsetIndexedErrors,
    };
  }

  onChangeFieldFrom = uniqueId => (field, eKey = 'value') => (e) => {
    this.setState({
      formsetIndexedDatasets: {
        ...this.state.formsetIndexedDatasets,
        [uniqueId]: {
          ...this.state.formsetIndexedDatasets[uniqueId],
          [field]: e.target[eKey],
        },
      },
    });
  }

  removeFilter = uniqueId => () => {
    this.setState({
      forms: _.filter(this.state.forms, form => uniqueId !== form),
      formsetIndexedDatasets: _.omit(this.state.formsetIndexedDatasets, uniqueId),
      formsetIndexedErrors: _.omit(this.state.formsetIndexedErrors, uniqueId),
    });
  }

  addFilter = (e) => {
    e.preventDefault();
    const newUniqueId = uuid4();
    this.setState({
      forms: [...this.state.forms, newUniqueId],
      formsetIndexedDatasets: {
        ...this.state.formsetIndexedDatasets,
        [newUniqueId]: {
          operator: 'and',
          filter_on: 'headword',
          filter: 'begins_with',
          query_string: '',
        },
      },
      formsetIndexedErrors: {
        ...this.state.formsetIndexedErrors,
        [newUniqueId]: {},
      },
    });
  }

  render() {
    const count = this.state.forms.length;
    return (
      <div>
        <input name="form-TOTAL_FORMS" value={count} id="id_form-TOTAL_FORMS" type="hidden" />
        <input name="form-INITIAL_FORMS" value="0" id="id_form-INITIAL_FORMS" type="hidden" />
        <input name="form-MIN_NUM_FORMS" value="0" id="id_form-MIN_NUM_FORMS" type="hidden" />
        <input name="form-MAX_NUM_FORMS" value="1000" id="id_form-MAX_NUM_FORMS" type="hidden" />

        {
          this.state.forms.map((uniqueId, i) => (
            <SearchForm
              i={i}
              key={uniqueId}
              dataset={this.state.formsetIndexedDatasets[uniqueId]}
              errors={this.state.formsetIndexedErrors[uniqueId]}
              onChangeFieldFrom={this.onChangeFieldFrom(uniqueId)}
              removeFilter={this.removeFilter(uniqueId)}
            />
          ))
        }

        <div className="form-group">
          <button type="submit" className="btn btn-success">{`${gettext('Buscar')}`}</button>
          <button className="btn btn-primary float-right" id="add-filter" onClick={this.addFilter}>
            {`${gettext('Agregar filtro')}`}
          </button>
        </div>
      </div>
    );
  }
}