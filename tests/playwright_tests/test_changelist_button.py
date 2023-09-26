import pytest
from django import forms
from django.http import HttpResponse
from django.urls import path, reverse
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person


class ChangelistForm(forms.Form):
    """Test form with a widget that adds a 'changelist' button."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person,
            url="autocomplete",
            changelist_url="changelist_page",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path(
        "changelist_button/", FormView.as_view(form_class=ChangelistForm, template_name="base.html"), name="changelist"
    ),
    path("changelist/", lambda r: HttpResponse("This is a dummy changelist page."), name="changelist_page"),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def changelist_button(dropdown_footer):
    """Return the changelist button in the dropdown footer."""
    return dropdown_footer.locator(".cl-btn")


@pytest.mark.parametrize("view_name", ["changelist"])
class TestChangelistButton:
    def test_has_visible_changelist_button(self, changelist_button):
        """Assert that the dropdown footer contains a visible 'changelist' button."""
        expect(changelist_button).to_be_visible()

    def test_changelist_query_string_contains_search_term(self, _page, changelist_button, search_input):
        """
        Assert that the URL to the changelist contains the current search term
        in the query string.
        """
        assert changelist_button.get_attribute("href") == reverse("changelist_page")
        with _page.expect_request_finished():
            search_input.fill("2022")
        assert "q=2022" in changelist_button.get_attribute("href")
