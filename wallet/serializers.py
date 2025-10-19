from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions

from decimal import Decimal
from .models import Wallet, Transaction

User = get_user_model()
class WalletBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('balance','currency')

class TransactionSerializer(serializers.Serializer):
    recipient = serializers.SlugRelatedField(
        slug_field='email',
        queryset=User.objects.all(),
        required=True
        )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('1.00'),
        required=True
    )

    def validate_recipient(self,recipient):
        user = self.context.get("request").user
        if recipient == user:
            raise serializers.ValidationError("Owner cannot be the recipient.")
        return recipient

    def create(self, validated_data):
        user = self.context.get("request").user
        source_wallet = user.wallet
        destination_wallet = validated_data['recipient'].wallet
        transaction_type = self.context.get("transaction_type")
        is_completed = self.context.get("is_completed",False)

        try:
            transaction = Transaction.objects.create(
                source_wallet=source_wallet,
                destination_wallet=destination_wallet,
                transaction_type = transaction_type,
                amount = validated_data["amount"],
                is_completed=is_completed
                )
        except Exception as e:
            raise exceptions.ErrorDetail(e)
        return transaction