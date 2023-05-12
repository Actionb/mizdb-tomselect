from typing import Any, Optional, Sequence, Tuple
from django import forms

# TODO: initially: only render selected choices


class MIZSelect(forms.Select):

    url = ''  # urlname 
    model = None
    create_field = ''  # model field to use to create new objects with

    value_field = ''  # TomSelect: valueField
    label_field = ''  # model field for the item labels  # TomSelect: labelField
    
    def __init__(self, model, url='autocomplete', create_field='', value_field='id', label_field='name', **kwargs):
        self.model = model
        self.url = url
        self.create_field = create_field
        self.value_field = value_field
        self.label_field = label_field
        super().__init__(**kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        opts = self.model._meta
        attrs.update({
            'is-tomselect': True,
            'data-autocomplete-url': self.url,
            'data-model': f"{opts.app_label}.{opts.model_name}",
            'data-value-field': self.value_field,
            'data-label-field': self.label_field,
            'data-create-field': self.create_field,
        })
        return attrs


class TabularMIZSelect(MIZSelect):
    """Display results in a table with a table header."""

    # dropdown header attributes
    value_field_label = ''  # TomSelect: valueFieldLabel
    label_field_label = ''  # TomSelect: labelFieldLabel

    # mapping of model field name to header label for additional columns
    extra_columns = None
    
    def __init__(self, *args, extra_columns=None, value_field_label='ID', label_field_label='Object', **kwargs):
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
            'data-extra-headers': ','.join(self.extra_columns.values()),
            'data-extra-columns': ','.join(self.extra_columns.keys()),
        })
        return attrs
    