import pytest
from django.urls import reverse

################################################################################
# Live server
################################################################################


@pytest.fixture
def get_url(live_server):
    """Return the URL for a given view name on the current live server."""

    def inner(view_name):
        return live_server.url + reverse(view_name)

    return inner


# NOTE: must not override original page fixture or tests can't be run against
# multiple browsers
@pytest.fixture
def _page(page, get_url, view_name):
    page.goto(get_url(view_name))
    return page


################################################################################
# Login
################################################################################


@pytest.fixture
def client_login(client):
    """Log in the given user into the django test client."""

    def inner(user):
        client.force_login(user)
        return client

    return inner


@pytest.fixture
def session_login(client_login, context):
    """
    Log in a user and add the session cookie for the logged-in user to the
    current context.
    """

    def inner(user):
        client = client_login(user)
        auth_cookie = client.cookies["sessionid"]
        pw_cookie = {
            "name": auth_cookie.key,
            "value": auth_cookie.value,
            "path": auth_cookie["path"],
            "domain": auth_cookie["domain"] or "localhost",
        }
        context.add_cookies([pw_cookie])

    return inner


@pytest.fixture
def login_perms_user(perms_user, session_login):
    """Log in a user with permissions."""
    session_login(perms_user)


@pytest.fixture
def login_noperms_user(noperms_user, session_login):
    """Log in a user without permissions."""
    session_login(noperms_user)


################################################################################
# Locators
################################################################################


@pytest.fixture
def ts_wrapper(_page):
    wrapper = _page.locator(".ts-wrapper")
    wrapper.wait_for()
    return wrapper


@pytest.fixture
def wrapper_click(_page, ts_wrapper):
    with _page.expect_request_finished():
        ts_wrapper.click()


@pytest.fixture
def search_input(_page, wrapper_click):
    search_input = _page.locator(".dropdown-input")
    search_input.wait_for()
    return search_input


@pytest.fixture
def search(_page, search_input):
    """Type a search term into the search input to start a search."""
    with _page.expect_request_finished():
        search_input.fill("Alice")


@pytest.fixture
def dropdown(_page):
    """Return a locator for the dropdown."""
    return _page.locator(".ts-dropdown")


@pytest.fixture
def dropdown_footer(_page, wrapper_click):
    """Return the dropdown footer."""
    return _page.locator(".dropdown-footer")


@pytest.fixture
def dropdown_items(_page):
    """Return all elements in the dropdown content."""
    return _page.locator(".ts-dropdown-content > *")


@pytest.fixture
def last_dropdown_item(dropdown_items):
    """Return the last item in the dropdown."""
    return dropdown_items.last


@pytest.fixture
def selectable_options(_page):
    """Return all selectable options."""
    return _page.locator("[data-selectable][role=option]")


@pytest.fixture
def select_options(select_count, search, selectable_options):
    """Select the first `select_count` options from the available options."""
    for i in range(select_count):
        selectable_options.all()[i].click()


@pytest.fixture
def selected(ts_control):
    """Return the locator for the selected items."""
    selected = ts_control.locator(".item")
    for item in selected.all():
        item.wait_for(state="attached")
    return selected


@pytest.fixture
def selected_values(selected):
    """Return a list of (locator, data-value) pairs of the selected items."""
    values = []
    for item in selected.all():
        values.append((item, item.get_attribute("data-value")))
    return values


@pytest.fixture
def ts_control(_page):
    return _page.locator(".ts-control")


@pytest.fixture
def remove_button():
    """Return a locator for the 'remove' button of the given item."""

    def inner(item):
        remove_button = item.locator(".remove")
        remove_button.wait_for(state="attached")
        return remove_button

    return inner


@pytest.fixture
def clear_button(ts_control):
    """Return a locator for the 'clear' button of the ts_control."""
    clear_button = ts_control.locator(".clear-button")
    clear_button.wait_for(state="attached")
    return clear_button
