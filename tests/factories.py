import factory

from tests.testapp.models import City, Person


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = factory.Faker("city")


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    full_name = factory.LazyAttribute(lambda o: f"{o.first_name} {o.last_name}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    dob = factory.Faker("date_of_birth")
    city = factory.SubFactory(CityFactory)
