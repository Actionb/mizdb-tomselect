from django import forms

from mizdb_tomselect.widgets import MIZSelect, TabularMIZSelect
from .models import Ausgabe


class Form(forms.Form):
    mizselect = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(Ausgabe, attrs={'class': 'form-control mb-3'}),
        required=False
    )
    mizselect_tabular = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=TabularMIZSelect(
            Ausgabe,
            extra_columns={'jahr': 'Jahr', 'num': 'Nummer', 'lnum': 'lfd.Nummer'},
            label_field_label='Ausgabe',
            attrs={'class': 'form-control mb-3'}
        ),
        required=False
    )

    # Multiple selection:
    mizselect_multiple = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelect(Ausgabe, attrs={'class': 'form-control mb-3'}, multiple=True),
        required=False
    )
    mizselect_tabular_multiple = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=TabularMIZSelect(
            Ausgabe,
            extra_columns={'jahr': 'Jahr', 'num': 'Nummer', 'lnum': 'lfd.Nummer'},
            label_field_label='Ausgabe',
            multiple=True,
            attrs={'class': 'form-control mb-3'}
        ),
        required=False
    )
