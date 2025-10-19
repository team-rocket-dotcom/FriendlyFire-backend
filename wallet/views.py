from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.views import Response, APIView
from rest_framework import status

from .serializers import WalletBalanceSerializer,TransactionSerializer
from .models import TransactionType
# Create your views here.

User = get_user_model()
class CheckBalanceView(GenericAPIView):
    http_method_names=['get']
    serializer_class = WalletBalanceSerializer

    def get(self, request,*args, **kwargs):
        user = request.user
        try:
            wallet = user.wallet
        except Exception as e:
            return Response({
                'detail':f'An error occured: {e}'
            })

        serializer = self.get_serializer(wallet)
        return Response(
            **serializer.data,
            status=status.HTTP_200_OK)

class TransferAmountView(APIView):
    def post(self,request,*args, **kwargs):
        serializer=TransactionSerializer(data=request.data,context={"request":request})
        if not serializer.is_valid():
            return Response({
                "detail":"Your request parameters did not validate.",
                "errors": serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)

        recipient = serializer.validated_data["recipient"]
        amount = serializer.validated_data["amount"]
        user = request.user
        sender_wallet = user.wallet
        recipient_wallet = recipient.wallet

        tx = None
        try:
            with transaction.atomic():
                tx = serializer.save(transaction_type = TransactionType.TRANSFER, is_completed=False)

                if sender_wallet.balance < amount:
                    raise ValueError("Insufficient Balance")

                sender_wallet.balance-=amount
                recipient_wallet.balance+=amount

                sender_wallet.save()
                recipient_wallet.save()

                tx.is_completed = True
                tx.save()
        except Exception as e:
            return Response({
                "detail":"Transaction failed.",
                "errors":str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "sender_balance": WalletBalanceSerializer(sender_wallet).data["balance"],
            "recipient_balance": WalletBalanceSerializer(recipient_wallet).data["balance"],
            "transaction_id": str(tx.id) if tx is not None else None
        })