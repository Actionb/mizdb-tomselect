from django import http
from django import views
from django.apps import apps

SEARCH_VAR = 'q'


class AutocompleteView(views.generic.list.BaseListView):
    """Query endpoint for TomSelect elements."""
    
    def setup(self, request, *args, **kwargs):
        super().setup(self, request, *args, **kwargs)
        self.model = apps.get_model(request.GET['model'])
        # TODO: set attributes from request parameters and kwargs
    
    def filter_queryset(self, queryset, q):
        return queryset.search(q)
    
    def get_results(self, q):
        for result in self.filter_queryset(self.get_queryset(), q).values():
            yield result

    def get(self, request, *args, **kwargs):
        # TODO: include pagination
        # TODO: check if should show create option
        data = {
            'results': list(self.get_results(request.GET.get(SEARCH_VAR, ''))),
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
        return self.model.objects.create(**{self.create_field: data[self.create_field]})
    
    def post(self, request, *args, **kwargs):
        if not self.has_add_permission(request):
            return http.HttpResponseForbidden()
        if request.POST.get(self.create_field) is None:
            return http.HttpResponseBadRequest()
        obj = self.create_object(request.POST)
        return http.JsonResponse({'pk': obj.pk, 'text': str(obj)})
    