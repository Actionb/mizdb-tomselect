# TomSelect for Django (MIZDB)

Django autocomplete widgets and views using [TomSelect](https://tom-select.js.org/).

Note that this library was written specifically with the [MIZDB](https://github.com/Actionb/MIZDB) app in mind - it may not apply to your app.

----
## Usage

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

Use the widgets:

```python
from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectTabular
from .models import MyModel


class MyForm(forms.Form):
    mizselect = forms.ModelChoiceField(
        MyModel.objects.all(),
        widget=MIZSelect(
            MyModel,
            url='my_autocomplete_view',
        ),
    )

    # Display results in a table, optionally with additional columns:
    mizselect_tabular = forms.ModelChoiceField(
        MyModel.objects.all(),
        widget=MIZSelectTabular(
            MyModel,
            url='my_autocomplete_view',
            # extra_columns is a mapping of model field: column header label for extra columns
            # (columns for valueField and labelField are always included)
            extra_columns={'name': 'Name', 'something_else': 'Something Else'},
            # The column header label for the labelField column
            label_field_label='My Model Objects',
        ),
    )
```

----
### Option creation
#### Add page link

The dropdown will include an 'Add' button if you pass the URL pattern name for
the add page of the given model to the widget:

```python
# urls.py
urlpatterns = [
    ...
    path('autocomplete/', AutocompleteView.as_view(), name='my_autocomplete_view'),
    path('my_model/add', MyModelAddView.as_view(), name='my_model_add'),
]

# forms.py
widget = MIZSelect(MyModel, url='my_autocomplete_view', add_url='my_model_add')
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

Override the view's `create_object` method to alter the creation process.

----
### Changelist link

The dropdown will include a link to the changelist of the given model if you
pass in the URL pattern name for the changelist.

```python
# urls.py
urlpatterns = [
    ...
    path('autocomplete/', AutocompleteView.as_view(), name='my_autocomplete_view'),
    path('my_model/change', MyModelChangelistView.as_view(), name='my_model_changelist'),
]

# forms.py
widget = MIZSelect(MyModel, url='my_autocomplete_view', changelist_url='my_model_changelist')
```

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
