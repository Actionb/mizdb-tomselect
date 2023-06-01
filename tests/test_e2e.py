import pytest
from django.urls import reverse
from playwright.sync_api import expect

from mizdb_tomselect.views import PAGE_SIZE
from testapp.models import Ausgabe

# Mark all tests in this module as end-to-end tests (excluded from running by default):
pytestmark = pytest.mark.e2e


@pytest.fixture(autouse=True)
def data():
    return [
        Ausgabe.objects.create(
            name=f"2022-{i + 1:02}",
            num=i + 1,
            lnum=100 + i,
            jahr="2022"
        )
        for i in range(PAGE_SIZE * 3)
    ]


@pytest.fixture
def first_object(data):
    return data[0]


@pytest.fixture
def page(page, live_server, view_name):
    page.goto(live_server.url + reverse(view_name))
    return page


@pytest.fixture
def ts_wrapper(page):
    wrapper = page.locator('.ts-wrapper')
    wrapper.wait_for()
    return wrapper


@pytest.fixture
def wrapper_focus(page, ts_wrapper):
    with page.expect_event('requestfinished'):
        ts_wrapper.click()  # TODO: .focus() should work too, but it doesnt


@pytest.fixture
def search_input(page, wrapper_focus):
    search_input = page.locator('.dropdown-input')
    search_input.wait_for()
    return search_input


@pytest.fixture
def search(page, search_input):
    with page.expect_event('requestfinished'):
        search_input.fill('2022')


def get_dropdown_items(page):
    """Return all elements in the dropdown."""
    return page.locator('.ts-dropdown-content > *')


def get_select_options(page):
    """Return all selectable options."""
    return page.locator('[data-selectable][role=option]')


def get_last_dropdown_item(page):
    item = None
    for item in get_dropdown_items(page).all():
        # Have to wait for each option to be attached, otherwise
        # test_virtual_scroll fails for the 'create' view.
        item.wait_for(state='attached')
    return item


@pytest.mark.parametrize('view_name', ['simple'])
def test_initially_empty(page, view_name):
    """Assert that the list of options is empty initially."""
    expect(get_dropdown_items(page)).to_have_count(0)


@pytest.mark.django_db
@pytest.mark.parametrize('view_name', ['simple'])
def test_load_first_results_on_focus(page, view_name, wrapper_focus):
    """Assert that the first page of options is loaded when the select gets focus."""
    expect(get_select_options(page)).to_have_count(PAGE_SIZE)


@pytest.mark.django_db
@pytest.mark.parametrize('view_name', ['simple', 'multiple', 'tabular', 'create'])
def test_virtual_scroll(page, view_name, search, data):
    """
    Assert that the user can scroll to the bottom of the options to load more
    options from the backend until there are no more search results to load.
    """
    expect(get_select_options(page)).to_have_count(PAGE_SIZE)

    # Second page:
    with page.expect_event('requestfinished'):
        get_last_dropdown_item(page).scroll_into_view_if_needed()
    expect(get_select_options(page)).to_have_count(PAGE_SIZE * 2)

    # Last page:
    with page.expect_event('requestfinished'):
        get_last_dropdown_item(page).scroll_into_view_if_needed()
    expect(get_select_options(page)).to_have_count(len(data))
    expect(get_last_dropdown_item(page)).to_have_text("Keine weiteren Ergebnisse")


@pytest.mark.django_db
@pytest.mark.parametrize('view_name', ['multiple'])
class TestSelectMultiple:

    @pytest.fixture
    def select_two(self, page, search):
        """Select the first two options."""
        options = get_select_options(page).all()
        options[0].click()
        options[1].click()

    @pytest.fixture
    def ts_control(self, page):
        return page.locator('.ts-control')

    @pytest.fixture
    def selected(self, page, select_two, ts_control):
        """Return the locator for the selected options."""
        return ts_control.locator('.item')

    def test_select_multiple(self, page, selected):
        """Assert that the user can select multiple options."""
        expect(selected).to_have_count(2)

    def test_has_remove_button(self, page, selected):
        """Assert that each selected option has a remove button."""
        for option in selected.all():
            expect(option.locator('.remove')).to_be_attached()

    def test_has_clear_button(self, page, ts_control):
        """Assert that the ts control has a clear all button."""
        expect(ts_control.locator('.clear-button')).to_have_count(1)


@pytest.mark.django_db
@pytest.mark.parametrize('view_name', ['tabular'])
class TestTabularSelect:

    @pytest.fixture
    def dropdown_header(self, page, wrapper_focus):
        """Return the dropdown header."""
        return page.locator('.ts-dropdown .dropdown-header')

    @pytest.fixture
    def header_columns(self, page, dropdown_header):
        """Return the column divs of the dropdown header."""
        return dropdown_header.locator('.row > *')

    @pytest.fixture
    def option_columns(self, page, wrapper_focus):
        """Return the column divs of a select option."""
        return get_select_options(page).first.locator('*')

    def test_has_dropdown_header(self, page, dropdown_header):
        """Assert that the dropdown has the expected table header."""
        expect(dropdown_header).to_be_attached()

    def test_header_columns(self, page, header_columns):
        """Assert that the dropdown header has the expected columns."""
        expect(header_columns).to_have_count(5)
        id_col, label_col, jahr_col, num_col, lnum_col = header_columns.all()
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text("ID")
        expect(label_col).to_have_class("col-5")
        expect(label_col).to_have_text("Ausgabe")
        expect(jahr_col).to_have_class("col")
        expect(jahr_col).to_have_text("Jahr")
        expect(num_col).to_have_class("col")
        expect(num_col).to_have_text("Nummer")
        expect(lnum_col).to_have_class("col")
        expect(lnum_col).to_have_text("lfd.Nummer")

    def test_options_have_columns(self, page, option_columns, first_object):
        """Assert that the data of the options are assigned to columns."""
        expect(option_columns).to_have_count(5)
        id_col, label_col, jahr_col, num_col, lnum_col = option_columns.all()
        expect(id_col).to_have_class("col-1")
        expect(id_col).to_have_text(str(first_object.pk))
        expect(label_col).to_have_class("col-5")
        expect(label_col).to_have_text(first_object.name)
        expect(jahr_col).to_have_class("col")
        expect(jahr_col).to_have_text(str(first_object.jahr))
        expect(num_col).to_have_class("col")
        expect(num_col).to_have_text(str(first_object.num))
        expect(lnum_col).to_have_class("col")
        expect(lnum_col).to_have_text(str(first_object.lnum))
