from unittest.mock import Mock, patch

import pytest
from django import forms
from django.db import models
from django.urls import path

from mizdb_tomselect.widgets import MIZSelect, MIZSelectMultiple, MIZSelectTabular, MIZSelectTabularMultiple
from tests.testapp.models import Person

urlpatterns = [
    path("test/autocomplete/", lambda r: None, name="autocomplete"),
    path("test/add/", lambda r: None, name="add_page"),
    path("test/edit/<path:object_id>/", lambda r: None, name="edit_page"),
    path("test/changelist/", lambda r: None, name="changelist_page"),
]

pytestmark = pytest.mark.urls(__name__)


@pytest.fixture
def make_widget(widget_class):
    """Return factory function that creates widgets of the given widget_class."""

    def inner(model=None, **kwargs):
        return widget_class(model=model, **kwargs)

    return inner


@pytest.fixture
def widget(make_widget, model=Person, **widget_kwargs):
    """Create a widget for the given model with the given kwargs."""
    return make_widget(model=model, **widget_kwargs)


@pytest.mark.parametrize("widget_class", [MIZSelect])
class TestMIZSelect:
    widget_class = MIZSelect

    def test_init_sets_default_value_field(self, make_widget):
        """
        Assert that init sets the default for `value_field` to the model's
        primary key.
        """

        class CustomPrimaryKeyModel(models.Model):
            my_primary_key = models.PositiveIntegerField(primary_key=True)

            class Meta:
                app_label = "testapp"

        widget = make_widget(model=CustomPrimaryKeyModel)
        assert widget.value_field == "my_primary_key"

    def test_init_sets_default_label_field_to_name(self, make_widget):
        """
        Assert that init sets the default for `label_field` to 'name' if the
        model has no `name_field`.
        """

        class NoNameFieldModel(models.Model):
            foo = models.CharField(max_length=1)

            class Meta:
                app_label = "testapp"

        widget = make_widget(model=NoNameFieldModel)
        assert widget.label_field == "name"

    def test_init_sets_default_label_field_to_name_field(self, make_widget):
        """
        Assert that init sets the default for `label_field` to the model's
        `name_field`.
        """

        class NameFieldModel(models.Model):
            foo = models.CharField(max_length=1)

            name_field = "foo"

            class Meta:
                app_label = "testapp"

        widget = make_widget(model=NameFieldModel)
        assert widget.label_field == "foo"

    def test_init_sets_default_search_lookup_from_label_field(self, make_widget):
        """
        Assert that init sets the default for `search_lookup` to the value of
        label_field + icontains.
        """
        widget = make_widget(model=Person, label_field="foo")
        assert widget.search_lookup == "foo__icontains"

    @pytest.mark.parametrize("selected", [[], [1], [42, 69]])
    def test_optgroups_filters_to_selected_options(self, widget, selected):
        """
        Assert that the choices queryset is filtered to only include the
        selected options.
        """
        mock_filter = Mock()
        mock_queryset = Mock(filter=mock_filter)
        with patch("mizdb_tomselect.widgets.super"):
            with patch.object(widget, "choices", new=Mock(queryset=mock_queryset)):
                widget.optgroups("name", selected)
                mock_filter.assert_called_with(pk__in=[str(c) for c in selected])

    def test_build_attrs(self, make_widget):
        """Assert that the required HTML attributes are added."""
        widget = make_widget(
            model=Person,
            url="autocomplete",
            value_field="pk",
            label_field="name",
            create_field="the_create_field",
            changelist_url="changelist_page",
            add_url="add_page",
            edit_url="edit_page",
        )
        attrs = widget.build_attrs({})
        assert attrs["is-tomselect"]
        assert attrs["data-autocomplete-url"] == "/test/autocomplete/"
        assert attrs["data-model"] == f"{Person._meta.app_label}.{Person._meta.model_name}"
        assert attrs["data-value-field"] == "pk"
        assert attrs["data-label-field"] == "name"
        assert attrs["data-create-field"] == "the_create_field"
        assert attrs["data-changelist-url"] == "/test/changelist/"
        assert attrs["data-add-url"] == "/test/add/"
        assert attrs["data-edit-url"] == "/test/edit/{pk}/"

    @pytest.mark.parametrize(
        "static_file",
        ("mizselect.css", "tom-select.bootstrap5.css", "mizselect.js"),
    )
    def test_media(self, widget, static_file):
        """Assert that the necessary static files are included."""
        assert static_file in str(widget.media)

    def test_get_url_fails_silently(self, widget):
        """Assert that _get_url fails silently when the view name cannot be reversed."""
        assert widget._get_url("this-cannot-be-reversed") == ""


@pytest.mark.parametrize("widget_class", [MIZSelectTabular])
class TestTabularMIZSelect:
    def test_init_sets_label_field_label(self, widget):
        """
        Assert that init sets the default for `label_field_label` to the
        verbose_name of the model.
        """
        assert widget.label_field_label == "Person"

    def test_init_sets_value_field_label(self, widget):
        """
        Assert that init sets the default for `value_field_label` to
        value_field.title().
        """
        assert widget.value_field_label == "Id"

    def test_build_attrs(self, make_widget):
        """Assert that the required HTML attributes are added."""
        widget = make_widget(
            model=Person,
            extra_columns={"dob": "Date of Birth", "city": "City"},
            value_field_label="Primary Key",
            label_field_label="Person",
        )
        attrs = widget.build_attrs({})
        assert attrs["is-tabular"]
        assert attrs["data-value-field-label"] == "Primary Key"
        assert attrs["data-label-field-label"] == "Person"
        assert attrs["data-extra-headers"] == '["Date of Birth", "City"]'
        assert attrs["data-extra-columns"] == '["dob", "city"]'


@pytest.mark.parametrize("widget_class", [MIZSelectMultiple])
class TestMIZSelectMultiple:
    def test_build_attrs(self, make_widget):
        """Assert that the required HTML attributes are added."""
        widget = make_widget(model=Person)
        attrs = widget.build_attrs({})
        assert attrs["is-multiple"]


@pytest.mark.parametrize("widget_class", [MIZSelectTabularMultiple])
class TestMIZSelectTabularMultiple:
    def test_build_attrs(self, make_widget):
        """Assert that the required HTML attributes are added."""
        widget = make_widget(model=Person)
        attrs = widget.build_attrs({})
        assert attrs["is-multiple"]


class SingleForm(forms.Form):
    field = forms.ModelChoiceField(Person.objects.all(), widget=MIZSelect(Person), required=False)


class MultipleForm(forms.Form):
    field = forms.ModelMultipleChoiceField(Person.objects.all(), widget=MIZSelectMultiple(Person), required=False)


@pytest.fixture
def bound_form(selected, select_mode):
    if select_mode == "single":
        return SingleForm(data={"field": selected[-1] if selected else None})
    else:
        return MultipleForm(data={"field": selected})


@pytest.fixture
def bound_widget(bound_form):
    """Return the widget of the form's bound field."""
    return bound_form["field"].field.widget


@pytest.fixture
def optgroups(selected, bound_widget):
    """Return the optgroups of the bound widget."""
    return bound_widget.optgroups("person", [str(pk) for pk in selected])


@pytest.fixture
def options(optgroups):
    """
    Return the list of options from the optgroups.

    The options are dictionaries as created by ChoiceWidget.create_option().
    """
    options = []
    for group in optgroups:
        name, subgroup, index = group
        for option in subgroup:
            options.append(option)
    return options


@pytest.mark.django_db
@pytest.mark.usefixtures("test_data")
class TestBoundForm:
    """Test MIZSelect widgets when used with a bound form."""

    @pytest.mark.parametrize("selected", [[], [1], [1, 5]])
    @pytest.mark.parametrize("select_mode", ["single", "multiple"])
    def test_is_valid(self, bound_form, selected, select_mode):
        """Assert that the form is valid for the given selected options."""
        assert bound_form.is_valid(), f"Form invalid. Errors: {bound_form.errors}"

    @pytest.mark.parametrize("selected", [[-1], [0], [1000]])
    @pytest.mark.parametrize("select_mode", ["single", "multiple"])
    def test_is_invalid(self, bound_form, selected, select_mode):
        """Assert that the form is invalid for the given selected options."""
        assert not bound_form.is_valid(), "Form unexpectedly valid."

    @pytest.mark.parametrize("selected", [[], [1], [1, 5]])
    @pytest.mark.parametrize("select_mode", ["single", "multiple"])
    def test_initial_options(self, test_data, options, selected, select_mode):
        """
        Assert that only the selected options are included in the widget's
        initial options.
        """
        option_values = sorted(str(o["value"]) for o in options)
        if select_mode == "single":
            # For single selects that aren't required the options will include
            # an 'empty option' with an empty string as value.
            option_values.pop(0)
        assert option_values == [str(pk) for pk in selected]
