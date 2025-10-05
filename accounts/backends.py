from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend, BaseBackend

from decouple import config

from google.oauth2 import id_token
from google.auth.transport import requests as google_req

User=get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        email= kwargs.get('email')
        password = kwargs.get('password')
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

class GoogleOAuthBackend(BaseBackend):
    def authenticate(self, request, *args, **kwargs):
        id_token_str=kwargs.get('id_token')
        if not id_token_str:
            return None

        try:
            user_info=id_token.verify_oauth2_token(
                id_token_str,
                google_req.Request(),
                audience=config('GOOGLE_CLIENT_ID')
            )

            social_id= user_info.get('sub')
            email= user_info.get('email')
            first_name = user_info.get('given_name')
            last_name = user_info.get('family_name')
            picture = user_info.get('picture')

        except:
            return None

        try:
            user= User.objects.get(email=email)

            update_fields=[]
            if first_name!=user.first_name:
                user.first_name=first_name
                update_fields.append('first_name')
            if last_name!=user.last_name:
                user.last_name=last_name
                update_fields.append('last_name')
            if picture!=user.picture:
                user.picture=picture
                update_fields.append('picture')

            if update_fields:
                user.save(update_fields)

            return user

        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                social_id=social_id,
                first_name=first_name,
                last_name=last_name,
                picture=picture,
                auth_provider='google'
            )

            return user
    
    def get_user(self, user_id):
        try:
            user= User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None