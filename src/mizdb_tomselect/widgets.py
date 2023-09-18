import copy
import json
from urllib.parse import unquote

from django import forms
from django.urls import NoReverseMatch, reverse


class MIZSelect(forms.Select):
    """
    A TomSelect widget with model object choices.

    The TomSelect element will be configured using custom data attributes on
    the select element, which are provided by the widget's `build_attrs` method.
    """

    def __init__(
        self,
        model,
        url="autocomplete",
        value_field="",
        label_field="",
        search_lookup="",
        create_field="",
        changelist_url="",
        add_url="",
        edit_url="",
        filter_by=(),
        can_remove=True,
        **kwargs,
    ):
        """
        Instantiate a MIZSelect widget.

        Args:
            model: the django model that the choices are derived from
            url: the view name of the view that serves the choices and
              handles requests from the TomSelect element
            value_field: the name of the model field that corresponds to the
              choice value of an option (f.ex. 'id'). Defaults to the name of
              the model's primary key field.
            label_field: the name of the model field that corresponds to the
              human-readable value of an option (f.ex. 'name'). Defaults to the
              value of the model's `name_field` attribute. If the model has no
              `name_field` attribute, it defaults to 'name'.
            search_lookup: a Django field lookup to use with the given search
              term to filter the results
            create_field: the name of the model field used to create new
              model objects with
            changelist_url: view name of the 'changelist' view for this model
            add_url: view name of the 'add' view for this model
            edit_url: view name of the 'change' view for this model
            filter_by: a 2-tuple (form_field_name, field_lookup) to filter the
              results against the value of the form field using the given
              Django field lookup. For example:
               ('foo', 'bar__id') => results.filter(bar__id=data['foo'])
            can_remove: if True, use the TomSelect Remove Button plugin
            kwargs: additional keyword arguments passed to forms.Select
        """
        self.model = model
        self.url = url
        self.value_field = value_field or self.model._meta.pk.name
        self.label_field = label_field or getattr(self.model, "name_field", "name")
        self.search_lookup = search_lookup or f"{self.label_field}__icontains"
        self.create_field = create_field
        self.changelist_url = changelist_url
        self.add_url = add_url
        self.edit_url = edit_url
        self.filter_by = filter_by
        self.can_remove = can_remove
        super().__init__(**kwargs)

    def optgroups(self, name, value, attrs=None):
        """Only query for selected model objects."""
        # inspired by dal.widgets.WidgetMixin from django-autocomplete-light
        selected_choices = [str(c) for c in value if c]
        all_choices = copy.copy(self.choices)
        # TODO: empty values in selected_choices will be filtered out twice
        self.choices.queryset = self.choices.queryset.filter(pk__in=[c for c in selected_choices if c])
        results = super().optgroups(name, value, attrs)
        self.choices = all_choices
        return results

    def _get_url(self, view_name, **kwargs):
        """
        Reverse the given view name and return the url.

        Fail silently if the url cannot be reversed.
        """
        if view_name:
            try:
                return reverse(view_name, **kwargs)
            except NoReverseMatch:
                pass
        return ""

    def get_url(self):
        """Hook to specify the autocomplete URL."""
        return self._get_url(self.url)

    def get_add_url(self):
        """Hook to specify the URL to the model's 'add' page."""
        return self._get_url(self.add_url)

    def get_edit_url(self):
        """Hook to specify the URL to the model's 'change' page."""
        return unquote(self._get_url(self.edit_url, args=["{pk}"]))

    def get_changelist_url(self):
        """Hook to specify the URL the model's 'changelist' page."""
        return self._get_url(self.changelist_url)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        opts = self.model._meta
        attrs.update(
            {
                "is-tomselect": True,
                "data-autocomplete-url": self.get_url(),
                "data-model": f"{opts.app_label}.{opts.model_name}",
                "data-search-lookup": self.search_lookup,
                "data-value-field": self.value_field,
                "data-label-field": self.label_field,
                "data-create-field": self.create_field,
                "data-changelist-url": self.get_changelist_url() or "",
                "data-add-url": self.get_add_url() or "",
                "data-edit-url": self.get_edit_url() or "",
                "data-filter-by": json.dumps(list(self.filter_by)),
                "can-remove": self.can_remove,
            }
        )
        return attrs

    class Media:
        css = {
            "all": ["vendor/tom-select/css/tom-select.bootstrap5.css", "mizdb_tomselect/css/mizselect.css"],
        }
        js = ["mizdb_tomselect/js/mizselect.js"]


class MIZSelectTabular(MIZSelect):
    """A MIZSelect widget that displays results in a table with a table header."""

    def __init__(self, *args, extra_columns=None, value_field_label="", label_field_label="", **kwargs):
        """
        Instantiate a MIZSelectTabular widget.

        Args:
            extra_columns: a mapping of <model field names> to <column labels>
              for additional columns. The field name tells TomSelect what
              values to look up on a model object result for a given column.
              The label is the table header label for a given column.
            value_field_label: table header label for the value field column.
              Defaults to value_field.title().
            label_field_label: table header label for the label field column.
              Defaults to the verbose_name of the model.
            args: additional positional arguments passed to MIZSelect
            kwargs: additional keyword arguments passed to MIZSelect
        """
        super().__init__(*args, **kwargs)
        self.value_field_label = value_field_label or self.value_field.title()
        self.label_field_label = label_field_label or self.model._meta.verbose_name or "Object"
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


class MultipleSelectionMixin:
    """Enable multiple selection with TomSelect."""

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build HTML attributes for the widget."""
        attrs = super().build_attrs(base_attrs, extra_attrs)  # noqa
        attrs["is-multiple"] = True
        return attrs


class MIZSelectMultiple(MultipleSelectionMixin, MIZSelect, forms.SelectMultiple):
    """A MIZSelect widget that allows multiple selection."""


class MIZSelectTabularMultiple(MultipleSelectionMixin, MIZSelectTabular, forms.SelectMultiple):
    """A MIZSelectTabular widget that allows multiple selection."""
