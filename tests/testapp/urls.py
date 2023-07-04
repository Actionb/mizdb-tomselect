from django.http import HttpResponse
from django.urls import path
from django.views.generic import FormView as BaseFormView

from mizdb_tomselect.views import AutocompleteView

from .forms import AddForm, ChangeForm, CreateForm, EditButtonForm, FilteredForm, MultipleForm, SimpleForm, TabularForm


def changelist_view(request):
    return HttpResponse("This is a dummy changelist page.")


def add_view(request):
    return HttpResponse("This is a dummy add page.")


def edit_view(request, object_id):
    return HttpResponse("This is a dummy edit page.")


class FormView(BaseFormView):
    template_name = "base.html"


urlpatterns = [
    path("simple/", FormView.as_view(form_class=SimpleForm), name="simple"),
    path("multiple/", FormView.as_view(form_class=MultipleForm), name="multiple"),
    path("tabular/", FormView.as_view(form_class=TabularForm), name="tabular"),
    path("create/", FormView.as_view(form_class=CreateForm), name="create"),
    path("with_add/", FormView.as_view(form_class=AddForm), name="add"),
    path("with_change/", FormView.as_view(form_class=ChangeForm), name="changelist"),
    path("filtered/", FormView.as_view(form_class=FilteredForm), name="filtered"),
    path("edit_button/", FormView.as_view(form_class=EditButtonForm), name="edit"),
    path("ac/", AutocompleteView.as_view(), name="ac"),
    path("add/", add_view, name="add_page"),
    path("edit/<path:object_id>/", edit_view, name="edit_page"),
    path("changelist/", changelist_view, name="changelist_page"),
]
