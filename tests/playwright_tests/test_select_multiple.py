import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelectMultiple
from tests.testapp.models import Person


class MultipleForm(forms.Form):
    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelectMultiple(
            model=Person,
            url="autocomplete",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("multiple/", FormView.as_view(form_class=MultipleForm, template_name="base.html"), name="multiple"),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["multiple"])
@pytest.mark.parametrize("select_count", [1, 2, 10])
@pytest.mark.usefixtures("test_data", "select_options")
class TestSelectMultiple:
    def test_select_multiple(self, selected, select_count):
        """Assert that the user can select multiple options."""
        expect(selected).to_have_count(select_count)

    def test_selected_items_have_remove_buttons(self, selected, remove_button):
        """Assert that each selected item has a remove button."""
        for item in selected.all():
            expect(remove_button(item)).to_be_visible()

    def test_has_clear_button(self, clear_button):
        """Assert that the ts control has a clear all button."""
        expect(clear_button).to_be_visible()
