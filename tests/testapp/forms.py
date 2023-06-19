from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectTabular

from .models import Ausgabe, Magazin

kwargs = {"model": Ausgabe, "url": "ac"}


class SimpleForm(forms.Form):
    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(**kwargs), required=False)


class MultipleForm(forms.Form):
    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(**kwargs, multiple=True), required=False)


class TabularForm(forms.Form):
    field = forms.ModelChoiceField(
        Ausgabe.objects.all(),
        widget=MIZSelectTabular(
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

    field = forms.ModelChoiceField(Ausgabe.objects.all(), widget=MIZSelect(changelist_url="changelist_page", **kwargs))


class FilteredForm(forms.Form):
    """
    Test form where the results of the 'ausgabe' field are filtered by the value
    of the 'magazin' field.
    """

    magazin = forms.ModelChoiceField(Magazin.objects.all())
    ausgabe = forms.ModelChoiceField(
        Ausgabe.objects.all(), widget=MIZSelect(filter_by=("magazin", "magazin_id"), **kwargs)
    )
