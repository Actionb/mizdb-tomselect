import re

import pytest
from django import forms
from django.urls import path, reverse
from django.views.generic import FormView, UpdateView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView, PopupResponseMixin
from mizdb_tomselect.widgets import MIZSelectMultiple
from tests.testapp.models import Person


class EditButtonForm(forms.Form):
    """Test form with a widget that adds 'edit' buttons to the selected items."""

    field = forms.ModelMultipleChoiceField(
        Person.objects.all(),
        widget=MIZSelectMultiple(
            model=Person,
            url="autocomplete",
            edit_url="edit_page",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


class PersonUpdateView(PopupResponseMixin, UpdateView):
    template_name = "base.html"
    model = Person
    fields = ["full_name"]
    success_url = "__SUCCESS_URL__"  # success url is irrelevant for popups


class InitialDataFormView(FormView):
    form_class = EditButtonForm
    template_name = "base.html"

    def get_initial(self):
        return {"field": [Person.objects.first(), Person.objects.last()]}


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("edit_button/", FormView.as_view(form_class=EditButtonForm, template_name="base.html"), name="edit"),
    path("edit_button_initial/", InitialDataFormView.as_view(), name="edit_initial"),
    path("edit/<path:pk>/", PersonUpdateView.as_view(), name="edit_page"),
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


@pytest.fixture
def edit_first_item(context, selected):
    """Open the change page of the first selected Person and rename them."""
    with context.expect_page() as new_page_info:
        get_edit_buttons(selected.first).click()
    new_page = new_page_info.value
    new_page.wait_for_load_state()
    new_page.get_by_label(re.compile("full name", re.IGNORECASE)).fill("Bob Testman")
    new_page.get_by_role("button").click()


@pytest.mark.parametrize("view_name", ["edit"])
@pytest.mark.parametrize("select_count", [1, 2, 10])
@pytest.mark.usefixtures("test_data", "select_options")
class TestEditButton:
    def test_adds_edit_button(self, edit_buttons, select_count):
        """Assert that an edit button is added to the selected items."""
        expect(edit_buttons).to_have_count(select_count)
        for btn in edit_buttons.all():
            expect(btn).to_be_visible()

    def test_edit_button_before_remove_button(self, selected, _page):
        """Assert that the edit button is positioned before the remove button."""
        for item in selected.all():
            assert item.evaluate(
                """div => {
                edit = div.querySelector(".edit")
                remove = div.querySelector(".remove")
                return edit.compareDocumentPosition(remove) == Node.DOCUMENT_POSITION_FOLLOWING
                }
                """
            )

    def test_edit_button_links_to_edit_page(self, edit_buttons, selected_values):
        """Assert that the edit button links to the edit page of the item."""
        for item, value in selected_values:
            expect(get_edit_buttons(item)).to_have_attribute("href", re.compile(reverse("edit_page", args=[value])))

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

    def test_edit_updates_selected_item(self, _page, selected, edit_first_item):
        """
        After successfully editing a related object, the selected item should be
        updated.
        """
        expect(selected.first).to_have_text("Bob Testman")


@pytest.mark.parametrize("view_name", ["edit_initial"])
@pytest.mark.usefixtures("test_data")
class TestEditButtonInitial:
    def test_initially_selected_edit_buttons(self, selected, edit_buttons):
        """Assert that initially selected items have edit buttons."""
        assert edit_buttons.count() == 2
        for item in selected.all():
            expect(get_edit_buttons(item)).to_have_count(1)

    def test_initial_edit_buttons_link_to_edit_page(self, edit_buttons, selected_values):
        """
        Assert that the edit buttons of the initially selected items link to
        their edit pages.
        """
        for item, value in selected_values:
            expect(get_edit_buttons(item)).to_have_attribute("href", re.compile(reverse("edit_page", args=[value])))
