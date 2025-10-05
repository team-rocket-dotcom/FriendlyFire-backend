from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, exceptions
from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
# Create your views here.

from .serializers import UserSerializer,SignUpSerializer, SignInSerializer, GoogleOAuthSerializer
from .tokens import get_tokens_for_user
from .mixins import AuthHandlerMixin

class SignUpView(GenericAPIView):
    http_method_names=['post']
    serializer_class=SignUpSerializer
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if not user:
            raise exceptions.APIException("Unable to create user")

        refresh_token,access_token = get_tokens_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": refresh_token,
            "access": access_token,
            "message":"User created successfully"
        }, status=status.HTTP_201_CREATED)

class SignInView(AuthHandlerMixin,GenericAPIView):
    http_method_names=['post']
    serializer_class=SignInSerializer
    permission_classes=[permissions.AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        return self.authenticate_and_respond(request,serializer)
    
class GoogleOAuthView(AuthHandlerMixin,GenericAPIView):
    http_method_names=['post']
    serializer_class=GoogleOAuthSerializer
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        return self.authenticate_and_respond(request,serializer)
    
class CustomTokenRefreshView(TokenRefreshView):
    def post(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({
                'detail':'token is not valid'
            },status=status.HTTP_401_UNAUTHORIZED)

        validated_data = serializer.validated_data

        refresh_token_object = RefreshToken(request.data['refresh'])
        user_id = refresh_token_object.get('user_id')

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except self.DoesNotExist:
            raise InvalidToken("User not found")
        
        return Response({
            **validated_data,
            "user":UserSerializer(user).data
        },status=status.HTTP_200_OK)