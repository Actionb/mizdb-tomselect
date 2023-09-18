import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelectTabular
from tests.testapp.models import Person


class TabularForm(forms.Form):
    """A test form with a tabular widget."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelectTabular(
            model=Person,
            url="autocomplete",
            label_field_label="Person",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


class ExtraColumnsForm(forms.Form):
    """A test form with a tabular widget that declares extra dropdown columns."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelectTabular(
            model=Person,
            url="autocomplete",
            extra_columns={"first_name": "First Name", "dob": "Date of Birth", "city__name": "City"},
            search_lookup="full_name__icontains",
            label_field="last_name",
            label_field_label="Last Name",
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("tabular/", FormView.as_view(form_class=TabularForm, template_name="base.html"), name="tabular"),
    path("extra/", FormView.as_view(form_class=ExtraColumnsForm, template_name="base.html"), name="extra"),
]


pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def dropdown_header(dropdown):
    """Return the dropdown header."""
    return dropdown.locator(".dropdown-header")


@pytest.fixture
def header_columns(dropdown_header):
    """Return the column divs of the dropdown header."""
    return dropdown_header.locator(".row > *")


@pytest.fixture
def option_columns(_page, wrapper_click, selectable_options):
    """Return the column divs of first selectable option."""
    return selectable_options.first.locator("*")


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["tabular"])
class TestTabularSelect:
    def test_has_dropdown_header(self, dropdown_header):
        """Assert that the dropdown has the expected table header."""
        expect(dropdown_header).to_be_attached()

    def test_header_columns(self, header_columns):
        """Assert that the dropdown header has the expected columns."""
        expect(header_columns).to_have_count(2)
        label_col, id_col = header_columns.all()
        expect(label_col).to_have_class("col")
        expect(label_col).to_have_text("Person")
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text("Id")

    def test_options_have_columns(self, random_person, option_columns):
        """Assert that the data of the options are assigned to columns."""
        expect(option_columns).to_have_count(2)
        label_col, id_col = option_columns.all()
        expect(label_col).to_have_class("col")
        expect(label_col).to_have_text(random_person.full_name)
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text(str(random_person.pk))


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["extra"])
class TestExtraColumns:
    def test_has_dropdown_header(self, dropdown_header):
        """Assert that the dropdown has the expected table header."""
        expect(dropdown_header).to_be_attached()

    def test_header_columns(self, header_columns):
        """Assert that the dropdown header has the expected columns."""
        expect(header_columns).to_have_count(5)
        label_col, first_name_col, dob_col, city_col, id_col = header_columns.all()
        expect(label_col).to_have_class("col-5")
        expect(label_col).to_have_text("Last Name")
        expect(first_name_col).to_have_class("col")
        expect(first_name_col).to_have_text("First Name")
        expect(dob_col).to_have_class("col")
        expect(dob_col).to_have_text("Date of Birth")
        expect(city_col).to_have_class("col")
        expect(city_col).to_have_text("City")
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text("Id")

    def test_options_have_columns(self, random_person, option_columns):
        """Assert that the data of the options are assigned to columns."""
        expect(option_columns).to_have_count(5)
        label_col, first_name_col, dob_col, city_col, id_col = option_columns.all()
        expect(label_col).to_have_class("col-5")
        expect(label_col).to_have_text(random_person.last_name)
        expect(first_name_col).to_have_class("col")
        expect(first_name_col).to_have_text(str(random_person.first_name))
        expect(dob_col).to_have_class("col")
        expect(dob_col).to_have_text(str(random_person.dob))
        expect(city_col).to_have_class("col")
        expect(city_col).to_have_text(str(random_person.city))
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text(str(random_person.pk))
