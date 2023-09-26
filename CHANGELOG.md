# Changelog

## [unreleased]

- added popup response that updates the form when modifying related objects via the add and edit buttons
- add init event to enable overwriting TomSelect parameters

## 0.7.1 (2023-09-19)

- rework scrolling when dropdown opens: only scroll when the bottom of the 
dropdown doesn't fit on the screen. The previous scrolling was 'too aggressive'.

## 0.7.0 (2023-09-18) 

- add `can_remove` widget argument which controls whether to include a remove button
- scroll dropdown into view when opening it
- remove edit buttons from tab order
- move id column for tabular selects to the end of a row. This should improve readability when the id column contains 'longer' values.
- (flex-)wrap buttons in the dropdown footer instead of having them overflow 

## 0.6.2 (2023-09-11)

- fail silently when add/edit/changelist URLs cannot be reversed

## 0.6.1 (2023-09-11)

- clicking on a selected item in a multi select now opens the dropdown instead of 
marking the item
- the mutation observer now checks children of added nodes

## 0.6.0 (2023-09-08)

- add separate init function which also checks whether the element is already initialized 
- added mutation observer to initialize inserted mizselect elements

## 0.5.1 (2023-09-06)

- use no_backspace_delete plugin by default
- change add button CSS class to `mizselect-add-btn` to make it more specific

## 0.5.0 (2023-07-17)

- add multiple selection variants of the widgets
- fix widget not rendering initially selected choices
- reworked demo
- fix edit button href not being set for initial items

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