import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import City, Person


class FilteredForm(forms.Form):
    """
    Test form where the results of the 'ausgabe' field are filtered by the value
    of the 'magazin' field.
    """

    city = forms.ModelChoiceField(City.objects.all())
    person = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person,
            url="autocomplete",
            filter_by=("city", "city_id"),
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("filtered/", FormView.as_view(form_class=FilteredForm, template_name="base.html"), name="filtered"),
]


pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def city_select(_page):
    select = _page.get_by_label("city")
    select.wait_for()
    return select


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["filtered"])
def test_options_filtered(
    new_york, random_city, new_york_people, _page, city_select, ts_wrapper, view_name, selectable_options
):
    """
    Assert that the options of the 'person' field are filtered with the values
    of the 'city' field.
    """
    city_select.select_option(value=str(random_city.pk))
    with _page.expect_request_finished():
        ts_wrapper.click()
    expect(selectable_options).to_have_count(0)
    city_select.focus()
    city_select.select_option(value=str(new_york.pk))
    with _page.expect_request_finished():
        ts_wrapper.click()
    expect(selectable_options).to_have_count(len(new_york_people))
