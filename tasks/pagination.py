from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import ValidationError

class TaskListPagination(CursorPagination):
    ordering=['-created_at','id']
    cursor_query_param='cursor'
    ordering_query_param = 'ordering'
    page_size=10
    max_page_size=50

    def get_ordering(self, request, queryset, view):
        client_ordering = request.query_params.get(self.ordering_query_param)
        if not client_ordering:
            return self.ordering

        valid_fields = getattr(view,'ordering_fields',[])
        if not valid_fields:
            valid_fields = [f.name for f in queryset.model._meta.fields]

        fields = [f.strip() for f in client_ordering.split(',') if f.strip()]
        for field in fields:
            field_name = field.lstrip('-')
            if field_name not in valid_fields:
                raise ValidationError(f"Invalid ordering field: {field_name}")

        return fields