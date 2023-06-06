from django.http import HttpResponse
from django.urls import path
from django.views.generic import FormView

from mizdb_tomselect.views import AutocompleteView

from .forms import AddForm, ChangeForm, CreateForm, MultipleForm, SimpleForm, TabularForm


def changelist_view(request):
    return HttpResponse("This is a dummy changelist page.")


def add_view(request):
    return HttpResponse("This is a dummy add page.")


urlpatterns = [
    path("simple/", FormView.as_view(form_class=SimpleForm, template_name="base.html"), name="simple"),
    path("multiple/", FormView.as_view(form_class=MultipleForm, template_name="base.html"), name="multiple"),
    path("tabular/", FormView.as_view(form_class=TabularForm, template_name="base.html"), name="tabular"),
    path("create/", FormView.as_view(form_class=CreateForm, template_name="base.html"), name="create"),
    path("with_add/", FormView.as_view(form_class=AddForm, template_name="base.html"), name="add"),
    path("with_change/", FormView.as_view(form_class=ChangeForm, template_name="base.html"), name="changelist"),
    path("ac/", AutocompleteView.as_view(), name="ac"),
    path("add/", add_view, name="add_page"),
    path("changelist/", changelist_view, name="changelist_page"),
]
