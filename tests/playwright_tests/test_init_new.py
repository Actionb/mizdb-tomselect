import re

import pytest
from django import forms
from django.urls import path
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect, MIZSelectMultiple, MIZSelectTabular, MIZSelectTabularMultiple
from tests.testapp.models import Person


class MIZSelectForm(forms.Form):
    # Create a field with a MIZSelect widget to include the widget media.
    field = forms.ModelChoiceField(Person.objects.all(), widget=MIZSelect(model=Person))


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("mizselect/", FormView.as_view(form_class=MIZSelectForm, template_name="base.html"), name="mizselect"),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def widget(widget_class, model=Person):
    """Return an instance of the given widget_class."""
    # widget.choices must be a ModelChoiceIterator, which requires a
    # form field. So create a ModelChoiceField form field and return
    # the widget created by the formfield.
    formfield = forms.ModelChoiceField(queryset=model.objects.all(), widget=widget_class(model))
    return formfield.widget


@pytest.fixture
def widget_html(widget):
    """Render the given widget."""
    return widget.render(name="new", value=None)


@pytest.fixture
def insert_html(_page, widget_html):
    """Insert the given html into the form element."""
    insert = """(form, html) => {
        const tpl = document.createElement('template')
        tpl.innerHTML = html.trim()
        form.appendChild(tpl.content.firstChild)
    }
    """
    _page.locator("form").evaluate(insert, widget_html)


@pytest.fixture
def new_element(_page, insert_html):
    """Return the newly inserted widget."""
    return _page.locator("[name=new]")


@pytest.mark.parametrize("view_name", ["mizselect"])
@pytest.mark.parametrize("widget_class", [MIZSelect, MIZSelectTabular, MIZSelectMultiple, MIZSelectTabularMultiple])
def test_new_elements_initialized(widget_class, view_name, new_element):
    """Assert that new, inserted mizselect elements get initialized."""
    expect(new_element).to_have_class(re.compile("tomselected"))
