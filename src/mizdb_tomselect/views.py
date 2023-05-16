from django import http
from django import views
from django.apps import apps

SEARCH_VAR = "q"
PAGE_VAR = "p"
PAGE_SIZE = 20


class AutocompleteView(views.generic.list.BaseListView):
    """Base list view for queries from TomSelect select elements."""

    paginate_by = PAGE_SIZE
    page_kwarg = PAGE_VAR
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.model = apps.get_model(request.GET['model'])
        # TODO: set attributes from request parameters and kwargs
    
    def filter_queryset(self, queryset, q):
        """Apply search filters on the result queryset."""
        return queryset.search(q)

    def order_queryset(self, queryset):
        """Apply ordering to the result queryset."""
        ordering = self.model._meta.ordering or ['id']
        return queryset.order_by(*ordering)
    
    def get_results(self, q):
        """Search for objects that match the search term and return the results."""
        queryset = self.filter_queryset(self.get_queryset(), q).values()
        return self.order_queryset(queryset)

    def get(self, request, *args, **kwargs):
        # TODO: check if should show create option
        queryset = self.get_results(request.GET.get(SEARCH_VAR, ''))
        page_size = self.get_paginate_by(queryset)
        _, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        data = {
            'results': list(page.object_list),
            'page': page.number,
            'has_more': page.has_next(),
            'is_paginated': is_paginated,
        }
        return http.JsonResponse(data)

    def has_add_permission(self, request):
        """Return True if the user has the permission to add a model object."""
        if request.user.is_authenticated:
            return False
        
        opts = self.model._meta
        codename = get_permission_codename('add', opts)
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
        return http.JsonResponse({'pk': obj.pk, 'text': str(obj)})
    