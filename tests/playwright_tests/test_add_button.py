import re
from urllib.parse import urlparse

import pytest
from django import forms
from django.urls import path
from django.views.generic import CreateView, FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView, PopupResponseMixin
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person, Genre


class AddForm(forms.Form):
    """Test form with a widget that adds an 'add' button."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person,
            url="autocomplete",
            add_url="add_page",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


class AddCreateForm(forms.Form):
    """Test form with a widget that enables option creation via AJAX."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person,
            url="autocomplete",
            add_url="add_page",
            create_field="full_name",
            search_lookup="full_name__icontains",
            label_field="full_name",
        ),
    )


class CreateUniqueForm(forms.Form):
    """Test form with a widget whose model has a unique constraint."""

    field = forms.ModelChoiceField(
        Genre.objects.all(),
        widget=MIZSelect(
            model=Genre,
            url="autocomplete",
            add_url="add_page",
            create_field="genre",
            search_lookup="genre__icontains",
            label_field="genre",
        ),
    )


class PersonCreateView(PopupResponseMixin, CreateView):
    template_name = "base.html"
    model = Person
    fields = ["full_name"]
    success_url = "__SUCCESS_URL__"  # success url is irrelevant for popups


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("add_button/", FormView.as_view(form_class=AddForm, template_name="base.html"), name="add"),
    path("create_button/", FormView.as_view(form_class=AddCreateForm, template_name="base.html"), name="create"),
    path("add/", PersonCreateView.as_view(), name="add_page"),
    path(
        "create_unique/", FormView.as_view(form_class=CreateUniqueForm, template_name="base.html"), name="create_unique"
    ),
]

pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def add_button(dropdown_footer):
    """Return the 'add' button in the dropdown footer."""
    return dropdown_footer.locator(".mizselect-add-btn")


@pytest.fixture
def requests_add_page(get_url):
    """
    Return a function that takes a request and checks whether the request is
    for the 'add' page.
    """

    def inner(request):
        return urlparse(request.url).path == urlparse(get_url("add_page")).path

    return inner


@pytest.fixture
def add_new_object(context, _page, add_button):
    """
    Create a new model object using the 'add' page.

    Click the add button, fill out the form of the popup, and submit the form.
    """
    with context.expect_page() as new_page_info:
        add_button.click()
    new_page = new_page_info.value
    new_page.wait_for_load_state()
    new_page.get_by_label(re.compile("full name", re.IGNORECASE)).fill("Bob Testman")
    new_page.get_by_role("button").click()


@pytest.mark.parametrize("view_name", ["add", "create"])
class TestAddButton:
    def test_add_button_visible(self, login_perms_user, add_button):
        """
        Assert that the 'add' button is visible for a user with the required
        permissions.
        """
        expect(add_button).to_be_visible()

    def test_add_button_invisible_when_no_permission(self, login_noperms_user, add_button):
        """
        Assert that the 'add' button is invisible if the user does not have
        the required permissions.
        """
        expect(add_button).not_to_be_visible()

    def test_add_button_invisible_for_unauthenticated_user(self, add_button):
        """Assert that 'add' button is invisible if no user is not logged in."""
        expect(add_button).not_to_be_visible()

    def test_footer_not_shown_when_add_btn_invisible(self, add_button, dropdown_footer):
        """
        Assert that the footer div is not shown if the 'add' button is
        invisible.
        """
        expect(add_button).not_to_be_visible()
        expect(dropdown_footer).not_to_be_visible()

    def test_add_button_text_changes_on_typing(self, login_perms_user, _page, add_button, search_input):
        """
        Assert that the text of the 'add' button updates along with the user
        typing in a search term.
        """
        expect(add_button).to_have_text("Add")
        with _page.expect_request_finished():
            search_input.fill("202")
        expect(add_button).to_have_text("Add: '202'")
        with _page.expect_request_finished():
            search_input.fill("2022")
        expect(add_button).to_have_text("Add: '2022'")


@pytest.mark.parametrize("view_name", ["add"])
class TestAddButtonClick:
    """Test with a button that opens a popup."""

    def test_add_button_click_no_search_term(self, login_perms_user, _page, add_button, requests_add_page):
        """
        Assert that clicking the 'add' button with no search term opens the
        'add' _page in a new tab.
        """
        with _page.expect_popup(requests_add_page):
            add_button.click()

    def test_add_button_click_no_create_field(
        self, login_perms_user, _page, add_button, search_input, requests_add_page
    ):
        """
        Assert that clicking the 'add' button with a search term but without
        a 'create_field' opens the 'add' page instead of starting a POST request.
        """
        with _page.expect_request_finished():
            search_input.fill("2022-99")
        with _page.expect_popup(requests_add_page):
            add_button.click()

    def test_add_updates_selection(self, _page, login_perms_user, add_new_object):
        """
        After adding a new object using the popup 'add' page, the created object
        should be immediately selected.
        """
        expect(_page.locator(".ts-control .item")).to_have_text("Bob Testman")


@pytest.mark.parametrize("view_name", ["create"])
class TestCreateButtonClick:
    """Test with a button that allows option creation via AJAX request."""

    def test_add_button_click_no_search_term(self, login_perms_user, _page, add_button, requests_add_page):
        """
        Assert that clicking the 'add' button with no search term opens the
        'add' page in a new tab.
        """
        with _page.expect_popup(requests_add_page):
            add_button.click()

    def test_add_button_click_create_field(self, login_perms_user, _page, add_button, search_input, get_url):
        """
        Assert that clicking the 'add' button starts a POST request with the
        search term if the widget declares a create_field.
        """
        with _page.expect_request_finished():
            search_input.fill("Bob Testman")
        with _page.expect_response(get_url("autocomplete")) as response_info:
            add_button.click()
        response = response_info.value
        data = response.json()
        assert data["text"] == "Bob Testman"
        assert data["pk"]

    def test_add_button_created_object_selected(self, login_perms_user, _page, add_button, search_input):
        """
        If the POST request to create a new object was successful, the created
        item should be immediately selected.
        """
        with _page.expect_request_finished():
            search_input.fill("Bob Testman")
        with _page.expect_request_finished():
            add_button.click()
        expect(_page.locator(".ts-control .item")).to_have_text("Bob Testman")
        expect(_page.locator(".dropdown-content")).not_to_be_visible()

    def test_no_popup_with_search_term(self, context, login_perms_user, _page, add_button, search_input):
        """
        Assert that clicking the 'add' button with a search term does not open
        the 'add' page.
        """
        with _page.expect_request_finished():
            search_input.fill("Bob Testman")
        with _page.expect_request_finished():
            add_button.click()
        assert len(context.pages) == 1

    def test_add_updates_selection(self, _page, login_perms_user, add_new_object):
        """
        After adding a new object using the popup 'add' page, the created object
        should be immediately selected.
        """
        expect(_page.locator(".ts-control .item")).to_have_text("Bob Testman")


@pytest.mark.parametrize("view_name", ["create_unique"])
class TestCreateUnique:
    def test_unique(self, login_perms_user, _page, add_button, search_input, dropdown):
        """
        Assert that the user is presenting with an alert if a unique constraint
        violation occurred with the 'create data'.
        """
        Genre.objects.create(genre="Rock")
        with _page.expect_request_finished():
            search_input.fill("Rock")
        add_button.click()
        alert = dropdown.get_by_text("Object already exists.")
        expect(alert).to_be_visible()
