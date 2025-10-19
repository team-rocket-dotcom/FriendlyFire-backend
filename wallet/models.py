from django.db import models
from django.conf import settings

import uuid
# Create your models here.

class CurrencyOptions(models.TextChoices):
    USD = 'usd', 'US Dollar'
    INR = 'inr', 'Indian Rupee'

class TransactionType(models.TextChoices):
    TRANSFER = 'trans', 'Transfer'
    DEPOSIT = 'depos', 'Deposit'
    WITHDRAWL = 'withd', 'Withdrawl'
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
        if not self.id:
            self.id=f'wallet{uuid.uuid4().hex[:10].lower()}'
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} {self.currency} {self.balance}"

class Transaction(models.Model):
    id = models.CharField(
        unique=True,
        editable=False,
        primary_key=True
    )
    source_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.DO_NOTHING,
        related_name='+'
        )
    destination_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.DO_NOTHING,
        related_name='+'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    transaction_type = models.CharField(
        choices=TransactionType.choices,
        max_length=5
    )
    is_completed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args, **kwargs):
        if not self.id:
            self.id=uuid.uuid4().hex
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.created_at}] {self.id} {self.get_transaction_type_display()} ₹{self.amount} from: {self.source_wallet} to: {self.destination_wallet} Status: {"SUCCESS" if self.is_completed else "FAILED"}"