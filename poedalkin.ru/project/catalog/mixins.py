from django.core.paginator import Paginator

class ListMixin:
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = int(request.GET.get("page", 1))
        by_page = int(request.GET.get("by_page", self.default_by_page))

        paginator = Paginator(queryset, by_page)

        page_obj = paginator.page(page)

        serializer = self.get_serializer(page_obj.object_list, many=True)

        result = {
            "page": page_obj.number, 
            "has_next": page_obj.has_next(),
            "data": serializer.data,
        }

        return result