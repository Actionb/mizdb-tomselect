import re

import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import PAGE_SIZE, PAGE_VAR, AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person


class MIZSelectForm(forms.Form):
    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person, url="autocomplete", search_lookup="full_name__icontains", label_field="full_name"
        ),
    )


class NoRemoveForm(forms.Form):
    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(model=Person, url="autocomplete", can_remove=False),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("mizselect/", FormView.as_view(form_class=MIZSelectForm, template_name="base.html"), name="mizselect"),
    path("noremove/", FormView.as_view(form_class=NoRemoveForm, template_name="base.html"), name="noremove"),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["mizselect"])
@pytest.mark.usefixtures("test_data")
class TestMIZSelect:
    def test_initially_empty(self, dropdown_items):
        """Assert that the list of options is empty initially."""
        expect(dropdown_items).to_have_count(0)

    def test_loads_first_page_on_click(self, _page, ts_wrapper, get_url, selectable_options):
        """Assert that clicking on the select loads the first page of results."""
        with _page.expect_request(re.compile(f"{get_url('autocomplete')}?.*{PAGE_VAR}=1.*")):
            ts_wrapper.click()
        expect(selectable_options).to_have_count(PAGE_SIZE)

    def test_virtual_scroll(self, _page, test_data, search, selectable_options, last_dropdown_item):
        """
        Assert that the user can scroll to the bottom of the options to load more
        options from the backend until there are no more search results to load.
        """
        expect(selectable_options).to_have_count(PAGE_SIZE)

        # Second _page:
        with _page.expect_request_finished():
            last_dropdown_item.scroll_into_view_if_needed()
        expect(selectable_options).to_have_count(PAGE_SIZE * 2)

        # Last _page:
        with _page.expect_request_finished():
            last_dropdown_item.scroll_into_view_if_needed()
        expect(selectable_options).to_have_count(len(test_data))
        expect(last_dropdown_item).to_have_text("Keine weiteren Ergebnisse")

    @pytest.mark.parametrize("select_count", [1])
    def test_selected_item_has_remove_button(self, select_options, selected, remove_button, select_count):
        """Assert that the selected item has a remove button."""
        expect(remove_button(selected.first)).to_be_attached()

    def test_has_dropdown_input(self, dropdown):
        """Assert that the dropdown contains an input element."""
        expect(dropdown.locator(".dropdown-input")).to_be_attached()

    def test_search_input_classes(self, search_input):
        """Assert that the search input has the expected classes."""
        expect(search_input).to_have_class(re.compile("form-control mb-1"))

    def test_dropdown_classes(self, dropdown):
        """Assert that the dropdown has the expected classes."""
        expect(dropdown).to_have_class(re.compile("p-2"))


@pytest.mark.django_db
@pytest.mark.usefixtures("test_data")
@pytest.mark.parametrize("select_count", [1])
@pytest.mark.parametrize("view_name", ["noremove"])
def test_can_remove_is_true(view_name, select_count, select_options, selected):
    """Assert that the selected item has no remove button if can_remove is True."""
    expect(selected.first.locator(".remove")).not_to_be_attached()
