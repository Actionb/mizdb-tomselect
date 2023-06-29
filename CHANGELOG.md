# Changelog

## [unreleased]

- set sensible defaults for widget attributes

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