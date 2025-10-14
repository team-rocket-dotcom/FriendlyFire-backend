from django.db import models
from django.conf import settings

# Create your models here.

class CurrencyOptions(models.TextChoices):
    USD = 'usd', 'US Dollar'
    INR = 'inr', 'Indian Rupee'
class Wallet(models.Model):

    id = models.CharField(
        unique=True,
        editable=False,
        primary_key=True
    )
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )

    balance = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=0.00,
    )

    currency = models.CharField(
        choices=CurrencyOptions.choices,
        max_length=3,
        default=CurrencyOptions.INR
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} {self.currency} {self.balance}"