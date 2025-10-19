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

