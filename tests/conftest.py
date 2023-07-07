import os

import pytest
from django.contrib.auth import get_permission_codename, get_user_model
from django.contrib.auth.models import Permission

from mizdb_tomselect.views import PAGE_SIZE
from tests.factories import CityFactory, PersonFactory
from tests.testapp.models import Person

# https://github.com/microsoft/playwright-python/issues/439
# https://github.com/microsoft/playwright-pytest/issues/29#issuecomment-731515676
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


################################################################################
# Model objects
################################################################################


@pytest.fixture
def perms_user():
    """Create a user that has 'add' permission for model Person."""
    user = get_user_model().objects.create_user(username="perms", password="foo")
    user.user_permissions.add(Permission.objects.get(codename=get_permission_codename("add", Person._meta)))
    return user


@pytest.fixture
def noperms_user():
    """Create a user that has no permissions."""
    return get_user_model().objects.create_user(username="noperms", password="bar")


@pytest.fixture
def random_city():
    return CityFactory.create()


@pytest.fixture
def random_person():
    return PersonFactory.create()


@pytest.fixture
def test_data():
    """Create three pages of test data."""
    return [PersonFactory.create(first_name="Alice") for i in range(PAGE_SIZE * 3)]


@pytest.fixture
def new_york():
    return CityFactory.create(name="New York")


@pytest.fixture
def new_york_people(new_york):
    return [PersonFactory.create(city=new_york) for i in range(10)]
