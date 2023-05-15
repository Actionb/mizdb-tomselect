from django.test import TestCase

from mizdb_tomselect.widgets import TabularMIZSelect, MIZSelect
from .models import Ausgabe


class TestMIZSelect(TestCase):

    def test_no_initial_choices(self):
        """Assert that the widget is rendered without any options."""
        widget = MIZSelect(model=Ausgabe)
        context = widget.get_context('ausgabe', None, {})
        self.assertFalse(context['widget']['optgroups'])

    def test_attrs(self):
        """Assert that the required HTML attributes are added."""
        widget = MIZSelect(
            model=Ausgabe,
            url='dummy_url',
            value_field='pk',
            label_field='num',
            create_field='the_create_field',
        )
        attrs = widget.build_attrs({})
        self.assertTrue(attrs['is-tomselect'])
        self.assertEqual(attrs['data-autocomplete-url'], 'dummy/url/'),
        self.assertEqual(attrs['data-model'], f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}")
        self.assertEqual(attrs['data-value-field'], 'pk')
        self.assertEqual(attrs['data-label-field'], 'num'),
        self.assertEqual(attrs['data-create-field'], 'the_create_field')


class TestTabularMIZSelect(TestCase):

    def test_attrs(self):
        """Assert that the required HTML attributes are added."""
        widget = TabularMIZSelect(
            model=Ausgabe,
            extra_columns={'jahr': 'Jahr', 'num': 'Nummer', 'lnum': 'lfd.Nummer'},
            value_field_label='Primary Key',
            label_field_label='Ausgabe',
        )
        attrs = widget.build_attrs({})
        self.assertEqual(attrs['is-tabular'], True)
        self.assertEqual(attrs['data-value-field-label'], 'Primary Key')
        self.assertEqual(attrs['data-label-field-label'], 'Ausgabe')
        self.assertEqual(attrs['data-extra-headers'], '["Jahr", "Nummer", "lfd.Nummer"]')
        self.assertEqual(attrs['data-extra-columns'], '["jahr", "num", "lnum"]')
