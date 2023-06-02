# TomSelect for MIZDB

Autocomplete widgets and views using TomSelect for the MIZDB app.

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

from mizdb_tomselect.widgets import MIZSelect, TabularMIZSelect
from .models import MyModel


class MyForm(forms.Form):
    mizselect = forms.ModelChoiceField(
        MyModel.objects.all(),
        widget=MIZSelect(
            MyModel, 
            url='my_autocomplete_view',
        ),
    )
    mizselect_tabular = forms.ModelChoiceField(
        MyModel.objects.all(),
        widget=TabularMIZSelect(
            MyModel,
            url='my_autocomplete_view',
            # extra_columns is a mapping of model field: column header label for extra columns
            # (besides the two columns for valueField and labelField)
            extra_columns={'name': 'Name', 'something_else': 'Something Else'},
            # The column header label for the labelField column
            label_field_label='My Model Objects',
        ),
    )
```

## Development & Demo

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```
Then see the demo for a preview: `python demo/manage.py runserver`

