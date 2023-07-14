from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectMultiple, MIZSelectTabular, MIZSelectTabularMultiple

from .models import Ausgabe, Magazin


class Form(forms.Form):
    mizselect = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(Ausgabe, changelist_url="changelist", add_url="add", create_field="name"),
        required=False,
    )
    mizselect_tabular = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectTabular(
            Ausgabe,
            extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"},
            label_field_label="Ausgabe",
            changelist_url="changelist",
            add_url="add",
            edit_url="edit",
        ),
        required=False,
    )

    # Multiple selection:
    mizselect_multiple = forms.ModelMultipleChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectMultiple(Ausgabe, changelist_url="changelist"),
        required=False,
    )
    mizselect_tabular_multiple = forms.ModelMultipleChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectTabularMultiple(
            Ausgabe,
            extra_columns={"jahr": "Jahr", "num": "Nummer", "lnum": "lfd.Nummer"},
            label_field_label="Ausgabe",
            add_url="add",
            create_field="name",
            edit_url="edit",
        ),
        required=False,
    )


class FilteredForm(forms.Form):
    magazin = forms.ModelChoiceField(queryset=Magazin.objects.all(), widget=MIZSelect(Magazin))
    ausgabe = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(
            Ausgabe,
            changelist_url="changelist",
            add_url="add",
            create_field="name",
            filter_by=("magazin", "magazin_id"),
        ),
        required=False,
    )
