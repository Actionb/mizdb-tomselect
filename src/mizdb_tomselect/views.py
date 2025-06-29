import json

from django import http, views
from django.apps import apps
from django.contrib.auth import get_permission_codename
from django.db import transaction, IntegrityError
from django.template.response import TemplateResponse

SEARCH_VAR = "q"
SEARCH_LOOKUP_VAR = "sl"
FILTERBY_VAR = "f"
VALUES_VAR = "vs"
IS_POPUP_VAR = "_popup"

PAGE_VAR = "p"
PAGE_SIZE = 20


class AutocompleteView(views.generic.list.BaseListView):
    """Base list view for queries from TomSelect select elements."""

    paginate_by = PAGE_SIZE
    page_kwarg = PAGE_VAR

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        request_data = getattr(request, request.method)
        self.model = apps.get_model(request_data["model"])
        self.create_field = request_data.get("create-field")
        self.search_lookup = request_data.get(SEARCH_LOOKUP_VAR)
        self.values_select = []
        if VALUES_VAR in request_data:
            self.values_select = json.loads(request_data[VALUES_VAR])
        self.q = request_data.get(SEARCH_VAR, "")

    def apply_filter_by(self, queryset):
        """
        Filter the given queryset against values set by other form fields.

        If the widget was set up with a `filter_by` parameter, the request will
        include the `FILTERBY_VAR` parameter, indicating that the results must
        be filtered against the lookup and value provided by `FILTERBY_VAR`.
        If `FILTERBY_VAR` is present but no value is set, return an empty
        queryset.
        """
        if FILTERBY_VAR not in self.request.GET:
            return queryset
        else:
            lookup, value = self.request.GET[FILTERBY_VAR].split("=")
            if not value:
                # A filter was set up for this autocomplete, but no filter value
                # was provided; return an empty queryset.
                return queryset.none()
            return queryset.filter(**{lookup: value})

    def search(self, queryset, q):
        """Filter the result queryset against the search term."""
        return queryset.filter(**{self.search_lookup: q})

    def order_queryset(self, queryset):
        """Order the result queryset."""
        ordering = self.model._meta.ordering or ["id"]
        return queryset.order_by(*ordering)

    def get_queryset(self):
        """Return a queryset of objects that match the search parameters and filters."""
        queryset = super().get_queryset()
        if self.q or FILTERBY_VAR in self.request.GET:
            queryset = self.apply_filter_by(queryset)
            queryset = self.search(queryset, self.q)
        return self.order_queryset(queryset)

    def get_page_results(self, page):
        """Hook for modifying the result queryset for the given page."""
        return page.object_list

    def get_result_values(self, results):
        """Return a JSON-serializable list of values for the given results."""
        return list(results.values(*self.values_select))

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        paginator, page, object_list, has_other_pages = self.paginate_queryset(queryset, page_size)
        data = {
            "results": self.get_result_values(self.get_page_results(page)),
            "page": page.number,
            "has_more": page.has_next(),
            "show_create_option": self.has_add_permission(request),
        }
        return http.JsonResponse(data)

    def has_add_permission(self, request):
        """Return True if the user has the permission to add a model object."""
        if not request.user.is_authenticated:
            return False

        opts = self.model._meta
        codename = get_permission_codename("add", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def create_object(self, data):
        """Create a new object with the given data."""
        return self.model.objects.create(**{self.create_field: data[self.create_field]})

    def _create_field_is_unique(self):  # pragma: no cover
        # Putting this call into a separate method makes mocking for the tests
        # easier.
        return self.model._meta.get_field(self.create_field).unique

    def post(self, request, *args, **kwargs):
        if not self.has_add_permission(request):
            return http.HttpResponseForbidden()
        if request.POST.get(self.create_field) is None:
            return http.HttpResponseBadRequest()
        try:
            with transaction.atomic():
                obj = self.create_object(request.POST)
        except IntegrityError:
            if self._create_field_is_unique():
                return http.JsonResponse({"error_type": "unique", "error_level": "warning"})
            else:
                # IntegrityError was not because of uniqueness, bail with a 500:
                return http.HttpResponseServerError()
        return http.JsonResponse({"pk": obj.pk, "text": str(obj)})


class PopupResponseMixin(views.generic.edit.ModelFormMixin):
    """
    A view mixin that handles the response for an add or edit popup.

    Upon posting a form, if IS_POPUP_VAR is present in the request data, return
    a TemplateResponse with the popup response template.
    That template loads a javascript that updates the form of the opener window
    that created the popup. The popup window or tab is then closed.

    To make use of this mixin:

        1. subclass your CreateView/UpdateView with it:

            class MyCreateView(PopupResponseMixin, CreateView):
                ...

        2. include a hidden field in the add/change form template to flag the
           form as a popup form:

            <form>
            ...
            {% if is_popup %}
                <input type="hidden" name="{{ is_popup_var }}" value="1">
            {% endif %}
            ...
            </form>

    """

    popup_response_template = "mizdb_tomselect/popup_response.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request  # noqa
        ctx["is_popup"] = IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET
        ctx["is_popup_var"] = IS_POPUP_VAR
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        request = self.request  # noqa
        if IS_POPUP_VAR in request.POST:
            return TemplateResponse(
                request,
                self.popup_response_template,
                {
                    "popup_response_data": json.dumps(
                        {
                            "value": str(self.object.serializable_value(self.object._meta.pk.attname)),
                            "text": str(self.object),
                        }
                    )
                },
            )
        return response
