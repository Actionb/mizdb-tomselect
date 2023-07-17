from django import forms

from mizdb_tomselect.widgets import MIZSelect, MIZSelectMultiple, MIZSelectTabular, MIZSelectTabularMultiple

from .models import City, Person


class MIZSelectForm(forms.Form):
    mizselect = forms.ModelChoiceField(Person.objects.all(), widget=MIZSelect(Person), required=False)


class MIZSelectTabularForm(forms.Form):
    mizselect_tabular = forms.ModelChoiceField(
        Person.objects.all(),
        label="Tabular with the default columns",
        widget=MIZSelectTabular(Person, label_field_label="Name"),
        required=False,
    )
    extra_columns = forms.ModelChoiceField(
        Person.objects.all(),
        label="Tabular with extra columns",
        widget=MIZSelectTabular(
            Person,
            extra_columns={"dob": "Date of Birth", "city__name": "City"},
            label_field_label="Name",
        ),
        required=False,
    )


class SelectMultipleForm(forms.Form):
    """Form with multiple selection."""

    MIZSelectMultiple = forms.ModelMultipleChoiceField(
        Person.objects.all(),
        widget=MIZSelectMultiple(Person),
        label="MIZSelectMultiple",
        required=False,
    )
    MIZSelectTabularMultiple = forms.ModelMultipleChoiceField(
        Person.objects.all(),
        widget=MIZSelectTabularMultiple(Person),
        label="MIZSelectTabularMultiple",
        required=False,
    )


class FilteredForm(forms.Form):
    """Form showing filtering by another form field."""

    city = forms.ModelChoiceField(queryset=City.objects.all(), widget=MIZSelect(City))
    person = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelectTabular(
            Person,
            extra_columns={"city__name": "City"},
            filter_by=("city", "city_id"),
            attrs={"data-placeholder": "Please select a city first"},
        ),
        required=False,
    )


class AddButtonForm(forms.Form):
    """Form showing the add button and option creation."""

    add_link = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            Person,
            add_url="admin:app_person_add",
            attrs={"data-placeholder": "Click the 'add' button"},
        ),
        label="Navigating to the 'add' page given by `add_url`",
        required=False,
    )
    via_ajax = forms.ModelChoiceField(
        Person.objects.all(),
        widget=MIZSelect(
            Person,
            add_url="admin:app_person_add",
            create_field="name",
            attrs={"data-placeholder": "Type a name and then click the 'add' button"},
        ),
        label="Using an AJAX request",
        required=False,
    )


class ChangelistButtonForm(forms.Form):
    """Form showing the changelist button."""

    person = forms.ModelChoiceField(
        Person.objects.all(), widget=MIZSelect(Person, changelist_url="admin:app_person_changelist")
    )


class EditButtonForm(forms.Form):
    """Form showing the edit buttons."""

    single = forms.ModelChoiceField(
        Person.objects.all(), widget=MIZSelect(Person, edit_url="admin:app_person_change"), required=False
    )
    multiple = forms.ModelMultipleChoiceField(
        Person.objects.all(), widget=MIZSelectMultiple(Person, edit_url="admin:app_person_change"), required=False
    )
