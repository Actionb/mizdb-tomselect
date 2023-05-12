from mizdb_tomselect.views import AutocompleteView


class ACView(AutocompleteView):
    
    def filter_queryset(self, queryset, q):
        return queryset.filter(name__icontains=q)
    