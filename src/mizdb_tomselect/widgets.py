import json

from django import forms
from django.urls import reverse


class MIZSelect(forms.Select):
    """A select widget for TomSelect with model object choices."""
    
    def __init__(self, model, url='autocomplete', value_field='id', label_field='name', create_field='', **kwargs):
        """
        Instantiate a MIZSelect widget.

        Args:
            model: the django model that the choices are derived from
            url: the URL pattern name of the view that serves the choices and
              handles requests from the TomSelect element
            value_field: the name of the field that has the choice value (i.e. 'id')
            label_field: the name of the field that contains the human-readable
              value for a choice
            create_field: the name of the field to use to create missing values
        """
        self.model = model
        self.url = url
        self.create_field = create_field
        self.value_field = value_field
        self.label_field = label_field
        super().__init__(**kwargs)

    def optgroups(self, name, value, attrs=None):
        return []  # Never provide any options; let the view serve the options.

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        opts = self.model._meta
        attrs.update({
            'is-tomselect': True,
            'data-autocomplete-url': reverse(self.url),
            'data-model': f"{opts.app_label}.{opts.model_name}",
            'data-value-field': self.value_field,
            'data-label-field': self.label_field,
            'data-create-field': self.create_field,
        })
        return attrs

    class Media:
        css = {
            "all": ['tom-select/dist/css/tom-select.bootstrap5.css',
                    'mizdb-tomselect/css/mizselect.css'],
        }
        js = ['tom-select/dist/js/tom-select.complete.js',
              'mizdb-tomselect/js/mizdb-tomselect-init.js']


class TabularMIZSelect(MIZSelect):
    """A TomSelect widget that displays results in a table with a table header."""
    
    def __init__(self, *args, extra_columns=None, value_field_label='ID', label_field_label='Object', **kwargs):
        """
        Instantiate a TabularMIZSelect widget.

        Args:
            extra_columns: a mapping of field names to column labels.
              The field name tells TomSelect what values to look up on a result.
              The label is the table header label for the column.
            value_field_label: table header label for the column of the value field
            label_field_label: table header label for the column of the label field
        """
        super().__init__(*args, **kwargs)
        self.value_field_label = value_field_label
        self.label_field_label = label_field_label
        self.extra_columns = extra_columns or {}

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.update({
            'is-tabular': True,
            'data-value-field-label': self.value_field_label,
            'data-label-field-label': self.label_field_label,
            'data-extra-headers': json.dumps(list(self.extra_columns.values())),
            'data-extra-columns': json.dumps(list(self.extra_columns.keys())),
        })
        return attrs
    