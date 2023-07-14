import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect, MIZSelectMultiple
from tests.testapp.models import Person


class SingleForm(forms.Form):
    mizselect = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person, url="autocomplete", search_lookup="full_name__icontains", label_field="full_name"
        ),
    )


class MultipleForm(forms.Form):
    mizselect = forms.ModelMultipleChoiceField(
        Person.objects.all(),
        widget=MIZSelectMultiple(
            model=Person,
            url="autocomplete",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


class SingleView(FormView):
    form_class = SingleForm
    template_name = "base.html"

    def get_initial(self):
        return {"mizselect": Person.objects.last()}


class MultipleView(FormView):
    form_class = MultipleForm
    template_name = "base.html"

    def get_initial(self):
        return {"mizselect": [Person.objects.last(), Person.objects.first()]}


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("single/", SingleView.as_view(), name="single"),
    path("multiple/", MultipleView.as_view(), name="multiple"),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.mark.urls(__name__)
@pytest.mark.parametrize("view_name", ["single", "multiple"])
@pytest.mark.usefixtures("test_data")
def test_initial_choices_selected(selected, view_name):
    """Assert that the initial choices are selected."""
    expected_count = 1 if view_name == "single" else 2
    assert selected.count() == expected_count
    if view_name == "single":
        assert selected.first.get_attribute("data-value") == str(Person.objects.last().pk)
    else:
        assert selected.first.get_attribute("data-value") == str(Person.objects.first().pk)
        assert selected.last.get_attribute("data-value") == str(Person.objects.last().pk)
