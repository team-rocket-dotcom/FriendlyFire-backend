from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Task, TodoListItem, PriorityLevel

User = get_user_model()
priority_options = [choice.value for choice in PriorityLevel]

class TodoListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoListItem
        fields = ('title','description')

class TaskSerializer(serializers.ModelSerializer):
    stake_amount = serializers.SerializerMethodField()
    todos = TodoListItemSerializer(many=True, required=False)
    recipient_id = serializers.PrimaryKeyRelatedField(
        source='stake_recipient',queryset=User.objects.all(), write_only=True, required=False
    )
    stake_recipient = UserSerializer(read_only=True)
    class Meta:
        model= Task
        fields=(
            'id',
            'title',
            'description',
            'due_date',
            'is_completed',
            'is_priority',
            'priority_level',
            'stake_amount',
            'stake_recipient',
            'is_penalty_processed',
            'recipient_id',
            'todos'
            )

    def get_stake_amount(self,obj):
        return obj.stake_amount

    def validate_due_date(self,due_date):
        if due_date and due_date < timezone.now():
            raise serializers.ValidationError("Due date cannot be in past")
        return due_date

    def validate(self, attrs):
        is_priority = attrs.get('is_priority',False)
        priority_level = attrs.get('priority_level',None)
        recipient_id = attrs.get('stake_recipient',None)

        if not is_priority:
            attrs.pop('priority_level',None)
            attrs.pop('recipient_id',None)
            return attrs

        if priority_level not in priority_options:
            raise serializers.ValidationError("Invalid priority level option")

        if priority_level is None or recipient_id is None:
            raise serializers.ValidationError('Priority Level and Stake recipient are required for Priority Tasks')

        return attrs

    @transaction.atomic
    def create(self,validated_data):
        todos_data = validated_data.pop('todos', None)
        user = self.context['request'].user

        task = Task.objects.create(
            owner = user,
            **validated_data
        )

        if todos_data:
            todos_to_create = [TodoListItem(task=task, **todo) for todo in todos_data]
            TodoListItem.objects.bulk_create(todos_to_create)
        return task

class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields=(
            'id',
            'title',
            'due_date',
            'is_completed',
            'is_priority',
            'priority_level'
        )