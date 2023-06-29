# TomSelect for Django (MIZDB)

Django autocomplete widgets and views using [TomSelect](https://tom-select.js.org/).

Note that this was written specifically with the [MIZDB](https://github.com/Actionb/MIZDB) app in mind - it may not apply to your app.
<!-- TOC -->
* [TomSelect for Django (MIZDB)](#tomselect-for-django-mizdb)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Widgets](#widgets)
    * [MIZSelect](#mizselect)
    * [MIZSelectTabular](#mizselecttabular)
  * [Function & Features](#function--features)
    * [Searching](#searching)
    * [Option creation](#option-creation)
      * [AJAX request](#ajax-request)
    * [Changelist link](#changelist-link)
    * [Filter against values of another field](#filter-against-values-of-another-field)
  * [Development & Demo](#development--demo)
<!-- TOC -->

----

## Installation

Install:
```bash
pip install -U mizdb-tomselect
```
## Usage

Add to installed apps:
```python
INSTALLED_APPS = [
    ...
    "mizdb_tomselect"
]
```

Configure an endpoint for autocomplete requests:

```python
# urls.py
from django.urls import path

from mizdb_tomselect.views import AutocompleteView

urlpatterns = [
    ...
    path('autocomplete/', AutocompleteView.as_view(), name='my_autocomplete_view')
]
```

Use the widgets in a form.

```python
from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectTabular
from .models import City, Person


class MyForm(forms.Form):
    city = forms.ModelChoiceField(
        City.objects.all(),
        widget=MIZSelect(City, url='my_autocomplete_view'),
    )

    # Display results in a table, with additional columns for fields 
    # 'first_name' and 'last_name':
    person = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelectTabular(
            Person,
            url='my_autocomplete_view',
            search_lookup="full_name__icontains",
            # for extra columns pass a mapping of model field: column header label
            extra_columns={'first_name': "First Name", "last_name": "Last Name"},
            # The column header label for the labelField column
            label_field_label='Full Name',
        ),
    )
``` 

NOTE: Make sure to include [bootstrap](https://getbootstrap.com/docs/5.2/getting-started/download/) somewhere. For example in the template:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MIZDB TomSelect Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
    {{ form.media }}
</head>
<body>
<div class="container">
    <form>
        {% csrf_token %}
        {{ form.as_div }}
        <button type="submit" class="btn btn-success">Save</button>
    </form>
</div>
</body>
</html>
```

----

## Widgets

The widgets pass attributes necessary to make autocomplete requests to the
HTML element via the dataset property. The TomSelect element is then initialized
from the attributes in the dataset property.

### MIZSelect

Base autocomplete widget. The arguments of MIZSelect are:

| Argument       | Default value                          | Description                                                                                    |
|----------------|----------------------------------------|------------------------------------------------------------------------------------------------|
| model          | **required**                           | the model class that provides the choices                                                      |
| url            | `"autocomplete"`                       | URL pattern name of the autocomplete view                                                      |
| value_field    | `f"{model._meta.pk.name}"`             | model field that provides the value of an option                                               |
| label_field    | `getattr(model, "name_field", "name")` | model field that provides the label of an option                                               |
| search_lookup  | `f"{label_field}__icontains"`          | the lookup to use when filtering the results                                                   |
| create_field   |                                        | model field to create new objects with ([see below](#ajax-request))                            |
| multiple       | False                                  | if True, allow selecting multiple options                                                      |
| changelist_url |                                        | URL name of the changelist view for this model ([see below](#changelist-link))                 |
| add_url        |                                        | URL name of the add view for this model([see below](#option-creation))                         |
| filter_by      |                                        | a 2-tuple defining an additional filter ([see below](#filter-against-values-of-another-field)) |


### MIZSelectTabular


This widget displays the results in tabular form. A table header will be added
to the dropdown. By default, the table contains two columns: one column for the choice 
value (commonly the "ID" of the option) and one column for the choice label (the 
human-readable part of the choice).

![Tabular select preview](./assets/mizselect_tabular.png "Tabular select preview")

MIZSelectTabular has the following additional arguments:

| Argument           | Default value                   | Description                         |
|--------------------|---------------------------------|-------------------------------------|
| extra_columns      |                                 | a mapping for additional columns    |
| value_field_label  | `f"{value_field.title()}"`      | table header for the value column   |
| label_field_label  | `f"{model._meta.verbose_name}"` | table header for the label column   |

#### Adding more columns 

To add more columns, pass a `result attribute name: column label` mapping to the widget
argument `extra_columns`.

The column label is the table header label for a given column.  

The attribute name tells TomSelect what value to look up on a result for the column.

**Important**: that means that the result visible to TomSelect must have an attribute
or property with that name or the column will remain empty. 
The results for TomSelect are created by the view calling `values()` on the 
result queryset, so you must make sure that the attribute name is available
on the view's root queryset as either a model field or as an annotation.

----

## Function & Features

### Searching

The AutocompleteView filters the result queryset against the `search_lookup`
passed to the widget. The default value for the lookup is `name__icontains`.
Overwrite the `AutocompleteView.search` method to modify the search process.
```python
class MyAutocompleteView(AutocompleteView):
    
    def search(self, request, queryset, q):
        # Filter using your own queryset method:
        return queryset.search(q)
```

### Option creation

To enable option creation in the dropdown, pass the URL pattern name of the 
add page of the given model to the widget. This will add an 'Add' button to the
bottom of the dropdown.

```python
# urls.py
urlpatterns = [
    ...
    path('autocomplete/', AutocompleteView.as_view(), name='my_autocomplete_view'),
    path('city/add/', CityAddView.as_view(), name='city_add'),
]

# forms.py
widget = MIZSelect(City, url='my_autocomplete_view', add_url='city_add')
```

Clicking on that button sends the user to the add page of the model.

#### AJAX request

If `create_field` was also passed to the widget, clicking on the button will
create a new object using an AJAX POST request to the autocomplete URL. The
autocomplete view will use the search term that the user put in on the
`create_field` to create the object:

```python
class AutocompleteView:
    
    def create_object(self, data):
        """Create a new object with the given data."""
        return self.model.objects.create(**{self.create_field: data[self.create_field]})
```

Override the view's `create_object` method to change the creation process.

### Changelist link

The dropdown will include a link to the changelist of the given model if you
pass in the URL pattern name of the changelist view.

```python
# urls.py
urlpatterns = [
    ...
    path('autocomplete/', AutocompleteView.as_view(), name='my_autocomplete_view'),
    path('city/change/', CityChangelistView.as_view(), name='city_changelist'),
]

# forms.py
widget = MIZSelect(City, url='my_autocomplete_view', changelist_url='city_changelist')
```

### Filter against values of another field

Use the `filter_by` argument to restrict the available options to the value of 
another field. The parameter must be a 2-tuple: `(name_of_the_other_form_field, django_field_lookup)`
```python
# models.py
class Person(models.Model):
    name = models.CharField(max_length=50)
    city = models.ForeignKey("City", on_delete=models.SET_NULL, blank=True, null=True)
    
class City(models.Model):
    name = models.CharField(max_length=50)
    is_capitol = models.BooleanField(default=False)

# forms.py
class PersonsFromCapitolsForm(forms.Form):
    capitol = forms.ModelChoiceField(queryset=City.objects.filter(is_capitol=True))
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=MIZSelect(
            Person,
            filter_by=("capitol", "city_id")
        )
    )
```
This will result in the Person result queryset to be filtered against 
`city_id` with the current value of the `capitol` formfield.  
NOTE: When using `filter_by`, the declaring element now **requires** that the other field 
provides a value. If the other field does not have a value, the search will not 
return any results.

----

## Development & Demo

```bash
python3 -m venv venv
source venv/bin/activate
make init
```

Then see the demo for a preview: `python demo/manage.py runserver`

Run tests with `make test` or `make tox`. To install required browsers for playwright: `playwright install`.
See the makefile for other commands.
