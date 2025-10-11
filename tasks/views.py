from rest_framework.viewsets import ModelViewSet

from .models import Task
from .serializers import TaskSerializer,TaskListSerializer
from .pagination import TaskListPagination
# Create your views here.

class TaskViewSet(ModelViewSet):
    pagination_class=TaskListPagination
    ordering_fields = ('due_date','priority_level','updated_at','created_at','id')

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)