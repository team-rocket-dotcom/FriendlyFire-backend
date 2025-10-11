from django.db import models
from django.conf import settings

import uuid
from decimal import Decimal
from decouple import config


# Create your models here.
class PriorityLevel(models.TextChoices):
    CRITICAL = 'C', "Critical"
    IMPORTANT = 'I', "Important"
    NORMAL = 'N', "Normal"

class Task(models.Model):
    STAKE_AMOUNTS = {
        PriorityLevel.CRITICAL: Decimal(config('CRITICAL_TASK_AMOUNT',cast=str)),
        PriorityLevel.IMPORTANT: Decimal(config('IMPORTANT_TASK_AMOUNT',cast=str)),
        PriorityLevel.NORMAL: Decimal(config('NORMAL_TASK_AMOUNT',cast=str))
    }

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        null=False,
        editable=False
        )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
        )

    title = models.CharField(max_length=50, null=False)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=False, blank=False)

    is_priority = models.BooleanField(default=False)
    priority_level = models.CharField(
        max_length=1,
        choices=PriorityLevel.choices,
        blank=True,
        null=True
    )
    stake_recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stake_amount_recipients'
    )
    is_penalty_processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def stake_amount(self):
        if self.is_priority and self.priority_level is not None:
            return self.STAKE_AMOUNTS.get(self.priority_level, Decimal('0.00'))
        return Decimal('0.00')

    def __str__(self):
        return self.title

class TodoListItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='todos'
    )