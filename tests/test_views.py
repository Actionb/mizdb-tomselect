import json
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.test import Client
from django.urls import reverse
from testapp.models import Ausgabe

from mizdb_tomselect.views import PAGE_SIZE, PAGE_VAR, SEARCH_VAR


@pytest.fixture
def obj():
    return Ausgabe.objects.create(name="Test", num="1", lnum="2", jahr="3")


@pytest.fixture(autouse=True)
def not_found():
    # Add a 'control' object that should never be included in the search results.
    return Ausgabe.objects.create(name="Not Found")


@pytest.fixture
def pages():
    # Create enough data for multiple pages.
    return [
        Ausgabe.objects.create(name=f"2022-{i + 1:02}", num=i + 1, lnum=100 + i, jahr="2022")
        for i in range(PAGE_SIZE * 2)
    ]


@pytest.fixture
def noperms_user():
    return get_user_model().objects.create_user(username="noperms", password="bar")


@pytest.mark.django_db
class TestAutocompleteView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("autocomplete")
        self.model_label = f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}"

    def test_get_contains_result(self, admin_client, obj):
        """The response of a search query should contain the expected result."""
        query_string = urlencode(
            {
                "model": self.model_label,
                SEARCH_VAR: "test",
            }
        )
        response = admin_client.get(f"{self.url}?{query_string}")
        data = json.loads(response.content)
        assert data["results"] == list(Ausgabe.objects.filter(pk=obj.pk).values())

    @pytest.mark.parametrize("page_number,has_more", [(1, True), (2, False)])
    def test_context_pagination(self, admin_client, pages, page_number, has_more):
        """
        The response of a search query should contain context items for
        pagination.
        """
        request_data = {
            "model": self.model_label,
            SEARCH_VAR: "2022",
            PAGE_VAR: str(page_number),
        }
        response = admin_client.get(self.url, data=request_data)
        data = json.loads(response.content)
        assert data["page"] == page_number
        assert data["has_more"] == has_more

    def test_post_creates_new_object(self, admin_client):
        """A successful POST request should create a new model object."""
        request_data = {
            "model": self.model_label,
            "name": "New Ausgabe",
            "create-field": "name",
        }
        response = admin_client.post(self.url, data=request_data)
        assert response.status_code == 200
        assert Ausgabe.objects.filter(name="New Ausgabe").exists()

    def test_post_context_contains_object_data(self, admin_client):
        """
        The context of a successful POST request should contain data about the
        created item.
        """
        request_data = {
            "model": self.model_label,
            "name": "New Ausgabe",
            "create-field": "name",
        }
        response = admin_client.post(self.url, data=request_data)
        new = Ausgabe.objects.get(name="New Ausgabe")
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
            "name": "New Ausgabe",
            "create-field": "name",
            "csrfmiddlewaretoken": token.coded_value if has_csrf_token else "",
        }
        response = client.post(self.url, data=request_data)
        if not has_csrf_token:
            assert response.status_code == 403
        else:
            assert response.status_code == 200
