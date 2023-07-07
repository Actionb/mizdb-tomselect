import pytest
from django import forms
from django.http import HttpResponse
from django.urls import path, reverse
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person


class EditButtonForm(forms.Form):
    """Test form with a widget that adds 'edit' buttons to the selected items."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person,
            url="autocomplete",
            edit_url="edit_page",
            search_lookup="full_name__icontains",
            label_field="full_name",
            multiple=True,
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("edit_button/", FormView.as_view(form_class=EditButtonForm, template_name="base.html"), name="edit"),
    path("edit/<path:object_id>/", lambda r, object_id: HttpResponse("This is a dummy edit page."), name="edit_page"),
]


pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


def get_edit_buttons(item):
    """Return the locator for the edit buttons."""
    edit_buttons = item.locator(".edit")
    for btn in edit_buttons.all():
        btn.wait_for(state="attached")
    return edit_buttons


@pytest.fixture
def edit_buttons(selected):
    """Return the edit buttons of the selected items."""
    return get_edit_buttons(selected)


@pytest.mark.parametrize("view_name", ["edit"])
@pytest.mark.parametrize("select_count", [1, 2, 10])
@pytest.mark.usefixtures("test_data", "select_options")
class TestEditButton:
    def test_adds_edit_button(self, edit_buttons, select_count):
        """Assert that an edit button is added to the selected items."""
        expect(edit_buttons).to_have_count(select_count)
        for btn in edit_buttons.all():
            expect(btn).to_be_visible()

    def test_edit_button_links_to_edit_page(self, edit_buttons, selected_values):
        """Assert that the edit button links to the edit page of the item."""
        for item, value in selected_values:
            expect(get_edit_buttons(item)).to_have_attribute("href", reverse("edit_page", args=[value]))

    def test_edit_button_opens_popup(self, _page, edit_buttons):
        """Assert that the edit button opens the edit page in a popup."""
        with _page.expect_popup():
            edit_buttons.first.click()

    def test_edit_button_click_no_dropdown(self, edit_buttons, dropdown, search_input):
        """
        Assert that clicking the edit button does not trigger the dropdown to
        appear.
        """
        search_input.blur()  # close the dropdown
        edit_buttons.first.click()
        expect(dropdown).not_to_be_visible()
