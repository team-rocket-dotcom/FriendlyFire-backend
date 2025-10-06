from django.urls import path
from .views import SignInView, SignUpView, GoogleOAuthView, CustomTokenRefreshView

urlpatterns = [
    path('sign-up',SignUpView.as_view(), name='sign-up'),
    path('sign-in',SignInView.as_view(), name='sign-in'),
    path('google',GoogleOAuthView.as_view(), name='google-oauth'),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token-refresh')
]