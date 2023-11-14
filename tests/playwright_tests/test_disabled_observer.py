import re

import pytest
from django import forms
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.urls import path
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person

template = """{% load static %}<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MIZDB TomSelect Testapp</title>
    <link href="{% static 'css/bootstrap.css' %}" rel="stylesheet">
    <script src="{% static 'js/bootstrap.bundle.js' %}"></script>
    {{ formset.media }}
    <script>
        addEventListener("DOMContentLoaded", () => {
            const btn = document.querySelector(".add-btn")
            btn.addEventListener("click", (e) => {
                e.preventDefault()

                const addRow = btn.parentNode
                const formset = addRow.parentNode

                const newForm = addRow.querySelector(".empty-form > div").cloneNode(true)
                formset.insertBefore(newForm, addRow)

                const prefix = "form"
                const index = document.querySelectorAll(".form-container").length
                const regex = new RegExp(`(${prefix}-(\\d+|__prefix__))`)
                newForm.querySelectorAll("select").forEach((elem) => {
                    const id = elem.getAttribute("id").replace(regex, `${prefix}-${index}`)
                    elem.setAttribute("id", id)
                })
            })
        })
    </script>
</head>
<body>
<div class="container">
    <form method="post">
        <div class="formset-container">
            {% for form in formset %}
                <div class="form-container row mb-3">{{ form.as_div }}</div>
            {% endfor %}
            <div class="add-row">
                <button type="button" class="btn-outline-success add-btn">Add another</button>
                <div class="empty-form d-none">
                    <div class="form-container row mb-3">{{ formset.empty_form.as_div }}</div>
                </div>
            </div>
        </div>
        <button type="submit" class="btn btn-success">Save</button>
    </form>
</div>
</body>
</html>
"""


class Form(forms.Form):
    field = forms.ModelChoiceField(Person.objects.all(), widget=MIZSelect(Person))


def view(request):
    context = RequestContext(request)
    context["formset"] = forms.formset_factory(Form, extra=1)()
    content = Template(template).render(context)
    return HttpResponse(content)


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("foo", view, name="foo"),
]


@pytest.fixture
def all_forms():
    """Return all forms of the given page."""

    def inner(p):
        # The empty form won't be selected with this since it is not a direct
        # child of .formset-container.
        return p.locator(".formset-container >.form-container")

    return inner


@pytest.fixture
def select_element():
    """Return the select element of the given form."""

    def inner(form):
        return form.locator("select")

    return inner


@pytest.fixture
def ts_wrapper():
    """Return the TomSelect wrapper div of the given form."""

    def inner(form):
        return form.locator(".ts-wrapper")

    return inner


@pytest.fixture
def add_form_button(_page):
    """Return the button that adds another formset form."""
    return _page.get_by_text("Add another")


@pytest.fixture
def disable():
    """Disable the given element."""

    def inner(elem):
        elem.evaluate("elem => elem.disabled = true")

    return inner


@pytest.fixture
def enable():
    """Enable the given element."""

    def inner(elem):
        elem.evaluate("elem => elem.disabled = false")

    return inner


pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.mark.usefixtures("test_data")
@pytest.mark.parametrize("view_name", ["foo"])
class TestLocked:
    def test_disable_select(self, _page, all_forms, select_element, ts_wrapper, disable):
        """
        Assert that disabling the select element also locks the TomSelect
        element.
        """
        form = all_forms(_page).first
        disable(select_element(form))
        expect(ts_wrapper(form)).to_have_class(re.compile("locked"))

    def test_disable_enable_select(self, _page, all_forms, select_element, ts_wrapper, disable, enable):
        """
        Assert that the TomSelect element is not locked after re-enabling a
        disabled select element.
        """
        form = all_forms(_page).first
        disable(select_element(form))
        enable(select_element(form))
        expect(ts_wrapper(form)).not_to_have_class(re.compile("locked"))

    def test_disable_select_of_new_form(self, _page, all_forms, add_form_button, select_element, ts_wrapper, disable):
        """
        Assert that disabling dynamically added select elements also locks the
        respective TomSelect elements.
        """
        add_form_button.click()
        form = all_forms(_page).last
        disable(select_element(form))
        expect(ts_wrapper(form)).to_have_class(re.compile("locked"))

    def test_disable_enable_select_of_new_form(
        self, _page, all_forms, add_form_button, select_element, ts_wrapper, disable, enable
    ):
        """
        Assert that the TomSelect element is not locked after re-enabling a
        disabled select element.
        """
        add_form_button.click()
        form = all_forms(_page).last
        disable(select_element(form))
        enable(select_element(form))
        expect(ts_wrapper(form)).not_to_have_class(re.compile("locked"))
