import json

from django import forms
from django.urls import reverse


class MIZSelect(forms.Select):
    """A select widget for TomSelect with model object choices."""

    def __init__(
        self,
        model,
        url="autocomplete",
        value_field="id",
        label_field="name",
        create_field="",
        multiple=False,
        changelist_url="",
        add_url="",
        **kwargs,
    ):
        """
        Instantiate a MIZSelect widget.

        Args:
            model: the django model that the choices are derived from
            url: the URL pattern name of the view that serves the choices and
              handles requests from the TomSelect element
            value_field: the name of the model field that corresponds to the
              choice value of an option (f.ex. 'id')
            label_field: the name of the model field that corresponds to the
              human-readable value of an option (f.ex. 'name')
            create_field: the name of the model field used to create new
              model objects with
            multiple: if True, allow selecting multiple options
            changelist_url: URL name of the changelist for this model
            add_url: URL name for the add page of this model
            kwargs: additional keyword arguments passed to forms.Select
        """
        self.model = model
        self.url = url
        self.create_field = create_field
        self.value_field = value_field
        self.label_field = label_field
        self.multiple = multiple
        self.changelist_url = changelist_url
        self.add_url = add_url
        super().__init__(**kwargs)

    def optgroups(self, name, value, attrs=None):
        return []  # Never provide any options; let the view serve the options.

    def get_url(self):
        """Hook to specify the autocomplete URL."""
        return reverse(self.url)

    def get_add_url(self):
        """Hook to specify the URL to the model's add page."""
        if self.add_url:
            return reverse(self.add_url)

    def get_changelist_url(self):
        """Hook to specify the URL the model's changelist."""
        if self.changelist_url:
            return reverse(self.changelist_url)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        opts = self.model._meta
        attrs.update(
            {
                "is-tomselect": True,
                "is-multiple": self.multiple,
                "data-autocomplete-url": self.get_url(),
                "data-model": f"{opts.app_label}.{opts.model_name}",
                "data-value-field": self.value_field,
                "data-label-field": self.label_field,
                "data-create-field": self.create_field,
                "data-changelist-url": self.get_changelist_url() or "",
                "data-add-url": self.get_add_url() or "",
            }
        )
        return attrs

    class Media:
        css = {
            "all": ["tom-select/dist/css/tom-select.bootstrap5.css", "mizdb-tomselect/css/mizselect.css"],
        }
        js = ["tom-select/dist/js/tom-select.complete.js", "mizdb-tomselect/js/mizdb-tomselect-init.js"]


class TabularMIZSelect(MIZSelect):
    """A TomSelect widget that displays results in a table with a table header."""

    def __init__(self, *args, extra_columns=None, value_field_label="ID", label_field_label="Object", **kwargs):
        """
        Instantiate a TabularMIZSelect widget.

        Args:
            extra_columns: a mapping of field names to column labels.
              The field name tells TomSelect what values to look up on a result.
              The label is the table header label for the column.
            value_field_label: table header label for the column of the value field
            label_field_label: table header label for the column of the label field
            args: additional positional arguments passed to MIZSelect
            kwargs: additional keyword arguments passed to MIZSelect
        """
        super().__init__(*args, **kwargs)
        self.value_field_label = value_field_label
        self.label_field_label = label_field_label
        self.extra_columns = extra_columns or {}

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.update(
            {
                "is-tabular": True,
                "data-value-field-label": self.value_field_label,
                "data-label-field-label": self.label_field_label,
                "data-extra-headers": json.dumps(list(self.extra_columns.values())),
                "data-extra-columns": json.dumps(list(self.extra_columns.keys())),
            }
        )
        return attrs
