from django.contrib.auth import authenticate
from rest_framework import exceptions, status
from rest_framework.views import Response

from .tokens import get_tokens_for_user

class AuthHandlerMixin:
    def authenticate_and_respond(self,request,serializer):
        serializer.is_valid(raise_exceptions=True)
        user = authenticate(request, **serializer.validated_data)

        if not user:
            raise exceptions.AuthenticationFailed("Invalid credentials")
        refresh_token, access_token = get_tokens_for_user(user)

        return Response({
            "refresh":refresh_token,
            "access":access_token,
            "message":"User signed-in successfully"
        },status=status.HTTP_200_OK)