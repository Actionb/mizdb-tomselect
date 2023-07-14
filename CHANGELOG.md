# Changelog

## [unreleased]

- add multiple selection variants of the widgets
- fix widget not rendering initially selected choices

## 0.4.0 (2023-07-10)

- add edit links to selected items

## 0.3.4 (2023-07-03)

- assign search term as AutocompleteView instance variable 'q'
- wrap create_object in an atomic block
- no longer call encodeURIComponent on values for query strings

## 0.3.3 (2023-06-29)

- fix dropdown footer being visible when it has no content (#2)
- set sensible defaults for widget attributes (#3, #4)

## 0.3.2 (2023-06-28)

- AutocompleteView: unquote search var string
- call values() on result queryset with fields specified on the widget only
  - this reduces query overhead 
  - allows including values from many-to-one relations

## 0.3.1 (2023-06-20)

- fix handling of undefined column data

## 0.3.0 (2023-06-20)

- refactor filterBy filtering in autocomplete view 
- add `search_lookup` argument to MIZSelect widget
- AutocompleteView now uses the `search_lookup` to filter the results

## 0.2.0 (2023-06-20)

- initial release