import pytest

from mizdb_tomselect.widgets import TabularMIZSelect, MIZSelect
from testapp.models import Ausgabe


class WidgetTestCase:
    widget_class = None

    @pytest.fixture(autouse=True)
    def make_widget(self):
        def _make_widget(model=Ausgabe, **kwargs):
            return self.widget_class(model, **kwargs)

        self.make_widget = _make_widget


class TestMIZSelect(WidgetTestCase):
    widget_class = MIZSelect

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
        )
        attrs = widget.build_attrs({})
        assert attrs["is-tomselect"]
        assert attrs["is-multiple"]
        assert attrs["data-autocomplete-url"] == "/dummy/url/"
        assert attrs["data-model"] == f"{Ausgabe._meta.app_label}.{Ausgabe._meta.model_name}"
        assert attrs["data-value-field"] == "pk"
        assert attrs["data-label-field"] == "num"
        assert attrs["data-create-field"] == "the_create_field"

    @pytest.mark.parametrize(
        "static_file",
        ("mizselect.css", "tom-select.bootstrap5.css", "mizdb-tomselect-init.js", "tom-select.complete.js"),
    )
    def test_media(self, static_file):
        """Assert that the necessary static files are included."""
        assert static_file in str(self.make_widget().media)


class TestTabularMIZSelect(WidgetTestCase):
    widget_class = TabularMIZSelect

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
