from django import http, views
from django.apps import apps
from django.contrib.auth import get_permission_codename

SEARCH_VAR = "q"
FILTERBY_VAR = "f"
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

    def filter_queryset(self, request, queryset, q):
        """Apply search filters on the result queryset."""
        filter_expected, filter_by = self.get_filter_by(request)
        if filter_expected and not filter_by:
            # A filter was set up for this autocomplete, but no filter value was
            # provided; return an empty queryset.
            return queryset.none()
        return queryset.filter(**filter_by).search(q)

    def order_queryset(self, queryset):
        """Apply ordering to the result queryset."""
        ordering = self.model._meta.ordering or ["id"]
        return queryset.order_by(*ordering)

    def get_filter_by(self, request):
        """
        Check whether FILTERBY_VAR is present in the request and prepare filter
        parameters.

        Returns a 2-tuple (boolean, dict). The boolean denotes whether filtering
        is expected, and the dict contains the filter parameters.
        """
        if FILTERBY_VAR not in request.GET:
            return False, {}
        else:
            required = True
            lookup, value = request.GET[FILTERBY_VAR].split("=")
            if not value:
                return required, {}
            return required, {lookup: value}

    def get_results(self, request):
        """
        Search for objects that match the search parameters and return the
        results as a values() queryset.
        """
        queryset = self.get_queryset()
        q = request.GET.get(SEARCH_VAR, "")
        if q or FILTERBY_VAR in request.GET:
            queryset = self.filter_queryset(request, queryset, q)
        return self.order_queryset(queryset.values())

    def get(self, request, *args, **kwargs):
        queryset = self.get_results(request)
        page_size = self.get_paginate_by(queryset)
        _, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        data = {
            "results": list(page.object_list),
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

    def post(self, request, *args, **kwargs):
        if not self.has_add_permission(request):
            return http.HttpResponseForbidden()
        if request.POST.get(self.create_field) is None:
            return http.HttpResponseBadRequest()
        obj = self.create_object(request.POST)
        return http.JsonResponse({"pk": obj.pk, "text": str(obj)})
