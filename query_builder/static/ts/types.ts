interface ControlledVocabFieldItem {
  label: string;
  value: string;
}

export interface ControlledVocabField {
  field: string;
  items: Array<ControlledVocabFieldItem>;
}

export interface FilterableField {
  field: string;
  label: string;
  terms: Array<string>;
  user_languages?: Array<string>;
}

export interface ExtraField {
  field: string;
  label: string;
  constraints?: Array<string>;
}

export interface FormDataset {
  query_string: string;
  operator: string;
  filter_on: string;
  filter: string;
  [extraValues: string]: string;
}

export interface SelectProps {
  onChange: (event: React.ChangeEvent) => void;
  value: string;
}
