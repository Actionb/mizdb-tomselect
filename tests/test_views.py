import json
from unittest.mock import Mock, patch
from urllib.parse import urlencode

import pytest
from django import forms
from django.db import IntegrityError
from django.db.models.sql.where import NothingNode
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
    HttpResponseServerError,
)
from django.template.response import TemplateResponse
from django.test import Client
from django.urls import path, reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import CreateView, UpdateView

from mizdb_tomselect.views import (
    FILTERBY_VAR,
    IS_POPUP_VAR,
    PAGE_VAR,
    SEARCH_LOOKUP_VAR,
    SEARCH_VAR,
    VALUES_VAR,
    AutocompleteView,
    PopupResponseMixin,
)
from tests.testapp.models import Person


@ensure_csrf_cookie
def csrf_cookie_view(request):
    # A dummy view to make the CSRF middleware set the CSRF cookie.
    return HttpResponse()


class PersonCreateView(PopupResponseMixin, CreateView):
    model = Person
    fields = forms.ALL_FIELDS
    template_name = "base.html"
    success_url = "__SUCCESS_URL__"


class PersonUpdateView(PopupResponseMixin, UpdateView):
    model = Person
    fields = forms.ALL_FIELDS
    template_name = "base.html"
    success_url = "__SUCCESS_URL__"


urlpatterns = [
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
    path("csrf/", csrf_cookie_view, name="csrf"),
    path("add/", PersonCreateView.as_view(), name="add_person"),
    path("edit/<path:pk>", PersonUpdateView.as_view(), name="edit_person"),
]


@pytest.fixture
def request_data():
    """Return additional request data as set by test parametrization."""
    return {}


def _make_request(rf_func, request_data):
    """Call the request factory function `rf_func` to create a request."""

    def inner(data=None, user=None, **extra):
        # Let data override the parametrized request data:
        request = rf_func("/", data={**request_data, **(data or {})}, **extra)
        if user:
            request.user = user
        return request

    return inner


@pytest.fixture
def get_request(rf, request_data):
    """Return a GET request."""
    return _make_request(rf.get, request_data)


@pytest.fixture
def post_request(rf, request_data):
    """Return a POST request."""
    return _make_request(rf.post, request_data)


@pytest.mark.django_db
@pytest.mark.urls(__name__)
class TestAutocompleteView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("autocomplete")
        self.model_label = f"{Person._meta.app_label}.{Person._meta.model_name}"

    def test_get_contains_result(self, admin_client, random_person):
        """The response of a search query should contain the expected result."""
        query_string = urlencode(
            {
                "model": self.model_label,
                SEARCH_VAR: random_person.full_name,
                SEARCH_LOOKUP_VAR: "full_name__icontains",
                VALUES_VAR: json.dumps(["id", "full_name"]),
            }
        )
        response = admin_client.get(f"{self.url}?{query_string}")
        data = json.loads(response.content)
        assert data["results"] == list(Person.objects.filter(pk=random_person.pk).values("id", "full_name"))

    @pytest.mark.parametrize("page_number,has_more", [(1, True), (2, True), (3, False)])
    def test_context_pagination(self, admin_client, test_data, page_number, has_more):
        """
        The response of a search query should contain context items for
        pagination.
        """
        request_data = {
            "model": self.model_label,
            SEARCH_VAR: "Alice",
            PAGE_VAR: str(page_number),
            SEARCH_LOOKUP_VAR: "full_name__icontains",
        }
        response = admin_client.get(self.url, data=request_data)
        data = json.loads(response.content)
        assert data["page"] == page_number
        assert data["has_more"] == has_more

    def test_post_creates_new_object(self, admin_client):
        """A successful POST request should create a new model object."""
        request_data = {"model": self.model_label, "full_name": "Bob Testman", "create-field": "full_name"}
        response = admin_client.post(self.url, data=request_data)
        assert response.status_code == 200
        assert Person.objects.filter(full_name="Bob Testman").exists()

    def test_post_context_contains_object_data(self, admin_client):
        """
        The context of a successful POST request should contain data about the
        created item.
        """
        request_data = {
            "model": self.model_label,
            "full_name": "Bob Testman",
            "create-field": "full_name",
        }
        response = admin_client.post(self.url, data=request_data)
        new = Person.objects.get(full_name="Bob Testman")
        data = json.loads(response.content)
        assert data["pk"] == new.pk
        assert data["text"] == str(new)

    def test_post_no_permission(self, client, noperms_user):
        """
        Users that do not have 'add' permission should have the POST request
        denied.
        """
        client.force_login(noperms_user)
        response = client.post(self.url, data={"model": self.model_label})
        assert isinstance(response, HttpResponseForbidden)

    def test_post_user_not_authenticated(self, client):
        """POST requests by unauthenticated users should be denied."""
        client.logout()
        response = client.post(self.url, data={"model": self.model_label})
        assert isinstance(response, HttpResponseForbidden)

    def test_post_create_field_data_missing(self, admin_client):
        """
        POST requests that do not provide a value for the 'create field' should
        be denied.
        """
        request_data = {
            "model": self.model_label,
            # 'name' is missing
            "create-field": "name",
        }
        response = admin_client.post(self.url, data=request_data)
        assert isinstance(response, HttpResponseBadRequest)

    @pytest.mark.parametrize("has_csrf_token", (True, False))
    def test_post_csrf(self, admin_user, has_csrf_token):
        """Assert that requests without a CSRF token are denied."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(admin_user)
        client.get(reverse("csrf"))  # have the csrf middleware set the cookie
        token = client.cookies["csrftoken"]

        request_data = {
            "model": self.model_label,
            "full_name": "Bob Testman",
            "create-field": "full_name",
            "csrfmiddlewaretoken": token.coded_value if has_csrf_token else "",
        }
        response = client.post(self.url, data=request_data)
        if not has_csrf_token:
            assert response.status_code == 403
        else:
            assert response.status_code == 200

    def test_get_no_search_term(self, client, random_person):
        """Assert that a GET request without a search term still returns results."""
        query_string = urlencode({"model": self.model_label, SEARCH_LOOKUP_VAR: "full_name__icontains"})
        response = client.get(f"{self.url}?{query_string}")
        data = json.loads(response.content)
        assert data["results"]

    def test_get_with_filter_by(self, client, random_person):
        """
        Assert that a GET request with a filterBy value returns the expected
        results.
        """
        query_string = urlencode(
            {
                "model": self.model_label,
                SEARCH_LOOKUP_VAR: "full_name__icontains",
                FILTERBY_VAR: f"city={random_person.city.pk}",
            }
        )
        response = client.get(f"{self.url}?{query_string}")
        data = json.loads(response.content)
        assert len(data["results"])
        assert random_person.pk in [r["id"] for r in data["results"]]

    def test_get_no_filter_by(self, test_data, client):
        """
        Assert that a GET request returns no results when a required filterBy
        has no value.
        """
        query_string = urlencode(
            {"model": self.model_label, SEARCH_LOOKUP_VAR: "full_name__icontains", FILTERBY_VAR: "city="}
        )
        response = client.get(f"{self.url}?{query_string}")
        data = json.loads(response.content)
        assert not data["results"]


@pytest.mark.django_db
class TestAutocompleteViewUnitTests:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = Person
        self.queryset = self.model.objects.all()
        self.model_label = f"{self.model._meta.app_label}.{self.model._meta.model_name}"

    @pytest.fixture
    def view(self, get_request):
        """Create an instance of AutocompleteView and assign the given request to it."""
        view = AutocompleteView()
        view.request = get_request()
        return view

    @pytest.fixture
    def setup_view(self, view, get_request):
        """Call the view's setup method with the given request."""
        # 'model' is required by setup()
        view.setup(request=get_request(data={"model": self.model_label}))

    @pytest.mark.parametrize("request_data", [{"model": f"{Person._meta.app_label}.{Person._meta.model_name}"}])
    def test_setup_sets_model(self, view, setup_view, request_data):
        """Assert that setup() sets the `model` attribute."""
        assert view.model == self.model

    @pytest.mark.parametrize("request_data", [{"create-field": "create_field"}])
    def test_setup_sets_create_field(self, view, setup_view, request_data):
        """Assert that setup() sets the `create_field` attribute."""
        assert view.create_field == "create_field"

    @pytest.mark.parametrize("request_data", [{SEARCH_LOOKUP_VAR: "search_lookup"}])
    def test_setup_sets_search_lookup(self, view, setup_view, request_data):
        """Assert that setup() sets the `search_lookup` attribute."""
        assert view.search_lookup == "search_lookup"

    @pytest.mark.parametrize("request_data", [{VALUES_VAR: json.dumps(["id", "full_name", "dob", "city"])}])
    def test_setup_sets_values_select(self, view, setup_view, request_data):
        """Assert that setup() sets the `values_select` attribute."""
        assert view.values_select == ["id", "full_name", "dob", "city"]

    @pytest.mark.parametrize("request_data", [{FILTERBY_VAR: "city_id=1"}])
    def test_apply_filter_by(self, view, request_data):
        """Assert that apply_filter_by applies the expected ^filter to the queryset."""
        queryset = view.apply_filter_by(self.queryset)
        assert len(queryset.query.where.children) == 1
        lookup = queryset.query.where.children[0]
        assert lookup.lhs.target == self.model._meta.get_field("city")
        assert lookup.rhs == 1

    @pytest.mark.parametrize("request_data", [{}])
    def test_apply_filter_by_no_filterby_var_in_request(self, view, request_data):
        """
        Assert that apply_filter_by returns the queryset unchanged if the
        request does not contain FILTERBY_VAR.
        """
        queryset = view.apply_filter_by(self.queryset)
        assert len(queryset.query.where.children) == 0

    @pytest.mark.parametrize("request_data", [{FILTERBY_VAR: "city_id="}])
    def test_apply_filter_by_no_filter_value(self, view, request_data):
        """
        Assert that apply_filter_by returns an empty queryset if no filter
        value is given.
        """
        queryset = view.apply_filter_by(self.queryset)
        assert len(queryset.query.where.children) == 1
        assert isinstance(queryset.query.where.children[0], NothingNode)

    def test_search(self, view):
        """Assert that search filters the queryset against the given search term."""
        view.search_lookup = "full_name__icontains"
        queryset = view.search(self.queryset, "Test")
        assert len(queryset.query.where.children) == 1
        lookup = queryset.query.where.children[0]
        assert lookup.lhs.target == self.model._meta.get_field("full_name")
        assert lookup.rhs == "Test"

    def test_order_queryset(self, view, setup_view):
        """Assert that order_queryset applies ordering to the queryset."""
        assert view.order_queryset(self.queryset).query.order_by == ("last_name", "first_name")

    @pytest.mark.parametrize("request_data", [{SEARCH_VAR: "Test", SEARCH_LOOKUP_VAR: "full_name__icontains"}])
    def test_get_queryset_calls_search(self, view, setup_view, request_data):
        """Assert that get_queryset calls search if a search term is given."""
        search_mock = Mock()
        with patch.object(view, "apply_filter_by", new=search_mock):
            view.get_queryset()
            search_mock.assert_called()

    @pytest.mark.parametrize("request_data", [{FILTERBY_VAR: "city_id=1", SEARCH_LOOKUP_VAR: "full_name__icontains"}])
    def test_get_queryset_calls_apply_filter_by(self, view, setup_view, request_data):
        """Assert that get_queryset calls apply_filter_by if FILTERBY_VAR is given."""
        apply_filter_by_mock = Mock()
        with patch.object(view, "apply_filter_by", new=apply_filter_by_mock):
            view.get_queryset()
            apply_filter_by_mock.assert_called()

    def test_get_queryset_calls_order_queryset(self, view, setup_view):
        """Assert that get_queryset calls order_queryset."""
        order_queryset_mock = Mock()
        with patch.object(view, "order_queryset", new=order_queryset_mock):
            view.get_queryset()
            order_queryset_mock.assert_called()

    @pytest.mark.parametrize("request_data", [{VALUES_VAR: json.dumps(["id", "full_name", "dob", "city__name"])}])
    def test_get_result_values(self, view, setup_view, request_data, random_person):
        """Assert that get_result_values returns a list of queryset values."""
        results = view.get_result_values(self.queryset.filter(pk=random_person.pk))
        assert results == [
            {
                "id": random_person.pk,
                "full_name": random_person.full_name,
                "dob": random_person.dob,
                "city__name": random_person.city.name,
            }
        ]

    def test_get(self, view, setup_view, admin_user):
        """Assert that get returns the expected response."""
        view.request.user = admin_user
        response = view.get(view.request)
        assert isinstance(response, JsonResponse)
        data = json.loads(response.content)
        assert "results" in data
        assert "page" in data
        assert "has_more" in data
        assert "show_create_option" in data

    @pytest.mark.parametrize("user_name, has_perm", [("noperms_user", False), ("perms_user", True)])
    def test_has_add_permission(self, request, view, setup_view, get_request, user_name, has_perm):
        """
        Assert that has_add_permission returns whether the user has 'add'
        permission for the given model.
        """
        _request = get_request
        _request.user = request.getfixturevalue(user_name)
        assert view.has_add_permission(_request) == has_perm

    @pytest.mark.parametrize("request_data", [{"create-field": "full_name"}])
    def test_create_object(self, view, setup_view, request_data):
        """Assert that create_object creates an object."""
        obj = view.create_object({"full_name": "Bob Testman"})
        assert isinstance(obj, self.model)
        assert obj.full_name == "Bob Testman"

    @pytest.mark.parametrize("request_data", [{"create-field": "name", "name": "__anything__"}])
    def test_post(self, view, setup_view, post_request, request_data):
        """Assert that post returns the expected response."""

        class DummyObject:
            pk = 42
            name = "foo"

            def __str__(self):
                return f"{self.name}"

        create_object_mock = Mock(return_value=DummyObject())

        with patch.object(view, "has_add_permission", new=Mock(return_value=True)):
            with patch.object(view, "create_object", new=create_object_mock):
                response = view.post(post_request())
                assert isinstance(response, JsonResponse)
                create_object_mock.assert_called()
                data = json.loads(response.content)
                assert data["pk"] == 42
                assert data["text"] == "foo"

    def test_post_no_permission(self, view, setup_view, noperms_user, post_request):
        """
        Assert that post returns a HttpResponseForbidden response when the user
        does not have permission to add objects.
        """
        assert isinstance(view.post(post_request(user=noperms_user)), HttpResponseForbidden)

    def test_post_no_create_field_data(self, view, setup_view, post_request):
        """
        Assert that post returns a HttpResponseBadRequest response when the
        request did not contain data for the create_field.
        """
        with patch.object(view, "has_add_permission", new=Mock(return_value=True)):
            assert isinstance(view.post(post_request(data={"create-field": "name"})), HttpResponseBadRequest)

    @pytest.mark.parametrize("request_data", [{"create-field": "full_name", "full_name": "Bob Testman"}])
    def test_post_unique_constraint(self, view, setup_view, post_request, request_data):
        """
        Assert that post returns a response with an error message if the user
        is attempting to use data on the create_field that would violate its
        unique constraints.
        """
        with patch.object(view, "has_add_permission", new=Mock(return_value=True)):
            with patch.object(view, "_create_field_is_unique", new=Mock(return_value=True)):
                with patch.object(view, "create_object", side_effect=IntegrityError):
                    response = view.post(post_request())
                    assert isinstance(response, JsonResponse)
                    data = json.loads(response.content)
                    assert data["error_type"] == "unique"
                    assert data["error_level"] == "warning"

    @pytest.mark.parametrize("request_data", [{"create-field": "full_name", "full_name": "Bob Testman"}])
    def test_post_integrity_error(self, view, setup_view, post_request, request_data):
        """
        Assert that post returns a HttpResponseServerError if create_object
        raises an IntegrityError and if the create_field is NOT unique.
        """
        with patch.object(view, "has_add_permission", new=Mock(return_value=True)):
            with patch.object(view, "_create_field_is_unique", new=Mock(return_value=False)):
                with patch.object(view, "create_object", side_effect=IntegrityError):
                    response = view.post(post_request())
                    assert isinstance(response, HttpResponseServerError)


@pytest.mark.django_db
@pytest.mark.urls(__name__)
class TestPopupResponseMixin:
    @pytest.mark.parametrize("action", ["add", "edit"])
    def test_redirects_success_url_when_not_a_popup(self, action, client, random_person):
        """
        Assert that the view redirects to the success_url when the view is not
        a popup.
        """
        if action == "add":
            url = reverse("add_person")
        else:
            url = reverse("edit_person", args=[random_person.pk])
        response = client.post(url, data={"full_name": "Bob Testman"})
        assert response.status_code == 302
        assert response.url == "__SUCCESS_URL__"

    def test_change_popup_response(self, client, random_person):
        """
        Assert that the correct response is returned after submitting a change
        popup.
        """
        response = client.post(
            reverse("edit_person", args=[random_person.pk]), data={"full_name": "Bob Testman", IS_POPUP_VAR: "1"}
        )
        assert isinstance(response, TemplateResponse)
        assert response.template_name == "mizdb_tomselect/popup_response.html"
        popup_data = json.loads(response.context_data["popup_response_data"])
        assert popup_data["value"] == str(random_person.pk)
        assert popup_data["text"] == "Bob Testman"

    def test_add_popup_response(self, client):
        """
        Assert that the correct response is returned after submitting an add
        popup.
        """
        response = client.post(reverse("add_person"), data={"full_name": "Bob Testman", IS_POPUP_VAR: "1"})
        assert isinstance(response, TemplateResponse)
        assert response.template_name == "mizdb_tomselect/popup_response.html"
        popup_data = json.loads(response.context_data["popup_response_data"])
        assert popup_data["value"] == "1"
        assert popup_data["text"] == "Bob Testman"
