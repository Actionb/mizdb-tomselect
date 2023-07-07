import pytest
from django import forms
from django.http import HttpResponse
from django.urls import path, reverse
from django.views.generic import FormView
from playwright.sync_api import expect

from mizdb_tomselect.views import AutocompleteView
from mizdb_tomselect.widgets import MIZSelect
from tests.testapp.models import Person


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


class NoFooterForm(forms.Form):
    """Test form with a field that has no dropdown footer."""

    field = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            model=Person, url="autocomplete", search_lookup="full_name__icontains", label_field="full_name"
        ),
    )


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("add_button/", FormView.as_view(form_class=AddForm, template_name="base.html"), name="add"),
    path("create_button/", FormView.as_view(form_class=AddCreateForm, template_name="base.html"), name="create"),
    path(
        "changelist_button/", FormView.as_view(form_class=ChangelistForm, template_name="base.html"), name="changelist"
    ),
    path("no_footer/", FormView.as_view(form_class=NoFooterForm, template_name="base.html"), name="no_footer"),
    path("add/", lambda r: HttpResponse("This is a dummy add page."), name="add_page"),
    path("changelist/", lambda r: HttpResponse("This is a dummy changelist page."), name="changelist_page"),
]


pytestmark = [pytest.mark.pw, pytest.mark.urls(__name__)]


@pytest.fixture
def dropdown_footer(_page, wrapper_click):
    """Return the dropdown footer."""
    return _page.locator(".dropdown-footer")


@pytest.fixture
def add_button(dropdown_footer):
    """Return the 'add' button in the dropdown footer."""
    return dropdown_footer.locator(".add-btn")


@pytest.fixture
def changelist_button(dropdown_footer):
    """Return the changelist button in the dropdown footer."""
    return dropdown_footer.locator(".cl-btn")


@pytest.fixture
def requests_add_page(get_url):
    """
    Return a function that takes a request and checks whether the request is
    for the 'add' page.
    """

    def inner(request):
        return request.url == get_url("add_page")

    return inner


@pytest.mark.parametrize(
    "view_name,has_footer", [("add", True), ("create", True), ("changelist", True), ("no_footer", False)]
)
def test_has_footer(view_name, has_footer, dropdown_footer, context):
    """
    Assert that a footer div is added to the dropdown content if the select
    element declares a 'changelist' URL or a 'add' URL.
    """
    if has_footer:
        # Note that the footer will be attached for an 'add' URL even if the
        # user has no 'add' permission.
        expect(dropdown_footer).to_be_attached()
    else:
        expect(dropdown_footer).not_to_be_attached()


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
        expect(add_button).to_have_text("Hinzufügen")
        with _page.expect_request_finished():
            search_input.fill("202")
        expect(add_button).to_have_text("'202' hinzufügen...")
        with _page.expect_request_finished():
            search_input.fill("2022")
        expect(add_button).to_have_text("'2022' hinzufügen...")


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


@pytest.mark.parametrize("view_name", ["create"])
class TestCreateButtonClick:
    """Test with a button that allows option creation via AJAX request."""

    def test_add_button_click_no_search_term(self, login_perms_user, _page, add_button, requests_add_page):
        """
        Assert that clicking the 'add' button with no search term opens the
        'add' _page in a new tab.
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
