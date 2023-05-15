import json
from urllib.parse import urlencode

from django.contrib.auth import get_user_model, get_permission_codename
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.test import TestCase, Client
from django.urls import reverse

from mizdb_tomselect.views import SEARCH_VAR, PAGE_VAR, PAGE_SIZE
from .models import Ausgabe


class TestAutocompleteView(TestCase):
    fixtures = ['data.json']

    @classmethod
    def setUpTestData(cls):
        cls.obj = Ausgabe.objects.create(name="Test", num="1", lnum="2", jahr="3")
        cls.not_found = Ausgabe.objects.create(name="Not Found")
        cls.perm_user = get_user_model().objects.create_user(username='hasperms', password='foo')
        perm = Permission.objects.get(
            codename=get_permission_codename('add', Ausgabe._meta),
            content_type=ContentType.objects.get_for_model(Ausgabe)
        )
        cls.perm_user.user_permissions.add(perm)
        cls.noperms_user = get_user_model().objects.create_user(username='noperms', password='bar')

    def setUp(self):
        self.client.force_login(self.perm_user)

    def test_get(self):
        """Assert that the response contains the expected result."""
        query_string = urlencode({
            SEARCH_VAR: 'test',
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}",
        })
        response = self.client.get(f"{reverse('autocomplete')}?{query_string}")
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertEqual(
            data['results'],
            list(Ausgabe.objects.filter(pk=self.obj.pk).values())
        )

    def test_get_pagination(self):
        """Test the pagination of the results."""
        paginator = Paginator(Ausgabe.objects.order_by('id').values(), PAGE_SIZE)
        request_data = {
            SEARCH_VAR: '2022',
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}",
            PAGE_VAR: '1',
        }

        response = self.client.get(reverse('autocomplete'), data=request_data)
        data = json.loads(response.content)
        self.assertIn('page', data)
        self.assertEqual(data['page'], 1)
        self.assertIn('has_more', data)
        self.assertTrue(data['has_more'])

        # Query for the last page:
        request_data[PAGE_VAR] = paginator.num_pages
        response = self.client.get(reverse('autocomplete'), data=request_data)
        data = json.loads(response.content)
        self.assertIn('page', data)
        self.assertEqual(data['page'], paginator.num_pages)
        self.assertIn('has_more', data)
        self.assertFalse(data['has_more'])

    def test_post(self):
        """Assert that a POST request creates the expected object."""
        request_data = {
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}",
            'name': 'New Ausgabe',
            'create-field': 'name',
        }
        response = self.client.post(reverse('autocomplete'), data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ausgabe.objects.filter(name='New Ausgabe').count(), 1)
        new = Ausgabe.objects.get(name='New Ausgabe')
        data = json.loads(response.content)
        self.assertIn('pk', data)
        self.assertEqual(data['pk'], new.pk)
        self.assertIn('text', data)
        self.assertEqual(data['text'], str(new))

    def test_post_no_permission(self):
        """
        Assert that requests to create objects are denied when the user does
        not have permission to add objects.
        """
        request_data = {
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}"
        }
        self.client.force_login(self.noperms_user)
        response = self.client.post(reverse('autocomplete'), data=request_data)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_post_user_not_authenticated(self):
        """POST requests by users that are not authenticated should be denied."""
        request_data = {
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}"
        }
        self.client.logout()
        response = self.client.post(reverse('autocomplete'), data=request_data)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_post_create_field_data_missing(self):
        """
        POST requests that do not provide a value for the 'create field' should
        be denied.
        """
        request_data = {
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}",
            # 'name' is missing
            'create-field': 'name'
        }
        response = self.client.post(reverse('autocomplete'), data=request_data)
        self.assertIsInstance(response, HttpResponseBadRequest)

    def test_post_csrf(self):
        """Assert that requests without a CSRF token are denied."""
        request_data = {
            'model': f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}",
            'name': 'New Ausgabe',
            'create-field': 'name',
        }

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.perm_user)
        client.get(reverse('csrf'))  # have the csrf middleware set the cookie
        token = client.cookies['csrftoken']

        response = client.post(reverse('autocomplete'), data=request_data)
        self.assertEqual(response.status_code, 403)

        request_data['csrfmiddlewaretoken'] = token.coded_value
        response = client.post(reverse('autocomplete'), data=request_data)
        self.assertEqual(response.status_code, 200)
