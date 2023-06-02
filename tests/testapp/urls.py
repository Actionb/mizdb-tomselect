from django.urls import path
from django.views.generic import FormView

from mizdb_tomselect.views import AutocompleteView
from .forms import SimpleForm, CreateForm, MultipleForm, TabularForm

urlpatterns = [
    path("simple/", FormView.as_view(form_class=SimpleForm, template_name="base.html"), name="simple"),
    path("multiple/", FormView.as_view(form_class=MultipleForm, template_name="base.html"), name="multiple"),
    path("tabular/", FormView.as_view(form_class=TabularForm, template_name="base.html"), name="tabular"),
    path("create/", FormView.as_view(form_class=CreateForm, template_name="base.html"), name="create"),
    path("ac/", AutocompleteView.as_view(), name="ac"),
]
