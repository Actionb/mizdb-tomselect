from django import forms

from mizdb_tomselect.widgets import MIZSelect, TabularMIZSelect
from .models import Ausgabe

kwargs = {"model": Ausgabe, "url": "ac", "attrs": {"testid": "mizselect"}}


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
