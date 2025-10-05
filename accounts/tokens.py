from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")
    
    refresh_token = RefreshToken.for_user(user)

    return str(refresh_token),str(refresh_token.access_token)