import pytest
from django.db import models
from testapp.models import Ausgabe

from mizdb_tomselect.widgets import MIZSelect, MIZSelectTabular


class WidgetTestCase:
    widget_class = None

    @pytest.fixture(autouse=True)
    def make_widget(self):
        def _make_widget(model=Ausgabe, **kwargs):
            return self.widget_class(model, **kwargs)

        self.make_widget = _make_widget


class TestMIZSelect(WidgetTestCase):
    widget_class = MIZSelect

    def test_init_sets_default_value_field(self):
        """
        Assert that init sets the default for `value_field` to the model's
        primary key.
        """

        class CustomPrimaryKeyModel(models.Model):
            my_primary_key = models.PositiveIntegerField(primary_key=True)

            class Meta:
                app_label = "testapp"

        widget = self.widget_class(CustomPrimaryKeyModel)
        assert widget.value_field == "my_primary_key"

    def test_init_sets_default_label_field_to_name(self):
        """
        Assert that init sets the default for `label_field` to 'name' if the
        model has no `name_field`.
        """

        class NoNameFieldModel(models.Model):
            foo = models.CharField(max_length=1)

            class Meta:
                app_label = "testapp"

        widget = self.widget_class(NoNameFieldModel)
        assert widget.label_field == "name"

    def test_init_sets_default_label_field_to_name_field(self):
        """
        Assert that init sets the default for `label_field` to the model's
        `name_field`.
        """

        class NameFieldModel(models.Model):
            foo = models.CharField(max_length=1)

            name_field = "foo"

            class Meta:
                app_label = "testapp"

        widget = self.widget_class(NameFieldModel)
        assert widget.label_field == "foo"

    def test_init_sets_default_search_lookup_from_label_field(self):
        """
        Assert that init sets the default for `search_lookup` to the value of
        label_field + icontains.
        """
        widget = MIZSelect(Ausgabe, label_field="foo")
        assert widget.search_lookup == "foo__icontains"

    def test_optgroups_no_initial_choices(self):
        """Assert that the widget is rendered without any options."""
        context = self.make_widget().get_context("ausgabe", None, {})
        assert not context["widget"]["optgroups"]

    def test_build_attrs(self):
        """Assert that the required HTML attributes are added."""
        widget = self.make_widget(
            model=Ausgabe,
            url="dummy_url",
            value_field="pk",
            label_field="num",
            create_field="the_create_field",
            multiple=True,
            changelist_url="changelist_page",
            add_url="add_page",
        )
        attrs = widget.build_attrs({})
        assert attrs["is-tomselect"]
        assert attrs["is-multiple"]
        assert attrs["data-autocomplete-url"] == "/dummy/url/"
        assert attrs["data-model"] == f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}"
        assert attrs["data-value-field"] == "pk"
        assert attrs["data-label-field"] == "num"
        assert attrs["data-create-field"] == "the_create_field"
        assert attrs["data-changelist-url"] == "/testapp/changelist/"
        assert attrs["data-add-url"] == "/testapp/add/"

    @pytest.mark.parametrize(
        "static_file",
        ("mizselect.css", "tom-select.bootstrap5.css", "mizselect.js"),
    )
    def test_media(self, static_file):
        """Assert that the necessary static files are included."""
        assert static_file in str(self.make_widget().media)


class TestTabularMIZSelect(WidgetTestCase):
    widget_class = MIZSelectTabular

    def test_init_sets_label_field_label(self):
        """
        Assert that init sets the default for `label_field_label` to the
        verbose_name of the model.
        """
        widget = self.widget_class(Ausgabe)
        assert widget.label_field_label == "Ausgabe"

    def test_init_sets_value_field_label(self):
        """
        Assert that init sets the default for `value_field_label` to
        value_field.title().
        """
        widget = self.widget_class(Ausgabe)
        assert widget.value_field_label == "Id"

    def test_build_attrs(self):
        """Assert that the required HTML attributes are added."""
        widget = self.make_widget(
            model=Ausgabe,
            extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"},
            value_field_label="Primary Key",
            label_field_label="Ausgabe",
        )
        attrs = widget.build_attrs({})
        assert attrs["is-tabular"]
        assert attrs["data-value-field-label"] == "Primary Key"
        assert attrs["data-label-field-label"] == "Ausgabe"
        assert attrs["data-extra-headers"] == '["Jahr", "Nummer", "lfd.Nummer"]'
        assert attrs["data-extra-columns"] == '["jahr", "num", "lnum"]'
