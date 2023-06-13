from django import forms

from mizdb_tomselect.widgets import MIZSelect, TabularMIZSelect

from .models import Ausgabe

kwargs = {"model": Ausgabe, "url": "ac"}


class SimpleForm(forms.Form):
    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(**kwargs), required=False)


class MultipleForm(forms.Form):
    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(**kwargs, multiple=True), required=False)


class TabularForm(forms.Form):
    field = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=TabularMIZSelect(
            **kwargs, extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"}, label_field_label="Ausgabe"
        ),
        required=False,
    )


class CreateForm(forms.Form):
    field = forms.ModelChoiceField(
        Ausgabe.objects.all(), widget=MIZSelect(**kwargs, create_field="name"), required=False
    )


class AddForm(forms.Form):
    """Test form with a widget with a 'add' URL."""

    field = forms.ModelChoiceField(
        Ausgabe.objects.all(), widget=MIZSelect(**kwargs, add_url="add_page", create_field="name")
    )


class ChangeForm(forms.Form):
    """Test form with a widget with a 'changelist' URL."""

    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(**kwargs, changelist_url="changelist_page"))
