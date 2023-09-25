"""Reminder: use the register decorator to add your view to the demo page."""

from collections import OrderedDict

from django.urls import path, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.views.generic import FormView as BaseFormView
from django.views.generic.base import ContextMixin

from mizdb_tomselect.views import AutocompleteView, PopupResponseMixin

from .forms import (
    AddButtonForm,
    ChangelistButtonForm,
    EditButtonForm,
    FilteredForm,
    MIZSelectForm,
    MIZSelectTabularForm,
    SelectMultipleForm,
)
from .models import Person


class DemoViewsRegistry:
    def __init__(self):
        self.views = OrderedDict()

    def register(self, view_class, name, label, description):
        self.views[view_class] = (name, label, description)

    def __iter__(self):
        for view_class, (name, label, description) in self.views.items():
            yield view_class, name, label, description

    @property
    def urls(self):
        urls = []
        for view_class, name, label, description in self:
            urls.append(path(f"{name}/", view_class.as_view(), name=name))
        return urls


demo_views = DemoViewsRegistry()


def register(name, label=None, description=None):
    """Add the decorated view to the demo views."""

    def inner(view_class):
        demo_views.register(view_class, name, label, description)

    return inner


class DemoAutocompleteView(AutocompleteView):
    """Endpoint for demo autocomplete requests."""

    def has_add_permission(self, request):
        return True  # no auth in this demo app


class DemoViewsMixin(ContextMixin):
    """A mixin that adds the demo views to the template context."""

    def get_context_data(self, **kwargs):
        return super().get_context_data(demo_views=list(demo_views), **kwargs)


class FormView(DemoViewsMixin, BaseFormView):
    template_name = "form.html"

    def get_initial(self):
        return dict(self.request.GET.lists())

    def get_context_data(self, **kwargs):
        description = demo_views.views[self.__class__][-1]
        return super().get_context_data(description=description, **kwargs)


class IndexView(DemoViewsMixin, TemplateView):
    template_name = "index.html"


@register("mizselect", "MIZSelect", "Demo of the basic MIZSelect widget")
class MIZSelectView(FormView):
    form_class = MIZSelectForm


@register("mizselect-tabular", "Tabular", "An example of the tabular version of the MIZSelect widget")
class MIZSelectTabularView(FormView):
    form_class = MIZSelectTabularForm


@register("select-multiple", "Multiple Selection", "An example of selecting multiple options")
class SelectMultipleView(FormView):
    form_class = SelectMultipleForm


@register("filtered", "Filtered", "An example of filtering against values of another form field")
class FilteredView(FormView):
    form_class = FilteredForm


@register("create-options", "Add Button", "Creating new options with the add button")
class AddButtonView(FormView):
    form_class = AddButtonForm


@register("changelist-button", "Changelist Button", "Adding a link to the changelist")
class ChangelistButtonView(FormView):
    form_class = ChangelistButtonForm


@register("edit-button", "Edit Buttons", "A form showing the edit buttons")
class EditButtonView(FormView):
    form_class = EditButtonForm


class PersonViewMixin:
    model = Person
    fields = ["name"]
    template_name = "model_form.html"
    success_url = reverse_lazy("index")


class PersonCreateView(PopupResponseMixin, PersonViewMixin, CreateView):
    pass


class PersonEditView(PopupResponseMixin, PersonViewMixin, UpdateView):
    pass
