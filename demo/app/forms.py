from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectTabular

from .models import Ausgabe


class Form(forms.Form):
    mizselect = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(
            Ausgabe,
            attrs={"class": "form-control mb-3"},
            changelist_url="changelist",
            add_url="add",
            create_field="name",
        ),
        required=False,
    )
    mizselect_tabular = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectTabular(
            Ausgabe,
            extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"},
            label_field_label="Ausgabe",
            attrs={"class": "form-control mb-3"},
            changelist_url="changelist",
            add_url="add",
        ),
        required=False,
    )

    # Multiple selection:
    mizselect_multiple = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(
            Ausgabe,
            attrs={"class": "form-control mb-3"},
            multiple=True,
            changelist_url="changelist",
        ),
        required=False,
    )
    mizselect_tabular_multiple = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectTabular(
            Ausgabe,
            extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"},
            label_field_label="Ausgabe",
            multiple=True,
            attrs={"class": "form-control mb-3"},
            add_url="add",
            create_field="name",
        ),
        required=False,
    )
