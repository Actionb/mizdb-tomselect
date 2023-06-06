from django.http import HttpResponse

from mizdb_tomselect.views import AutocompleteView


class DemoAutocompleteView(AutocompleteView):
    def has_add_permission(self, request):
        return True  # no auth in this demo app


def changelist_view(request):
    return HttpResponse("This is a dummy changelist page.")


def add_view(request):
    return HttpResponse("This is a dummy add page.")
