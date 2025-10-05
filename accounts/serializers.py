from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =('id','email','first_name','last_name','auth_provider','picture')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required= True)

    class Meta:
        model = User
        fields=('email','password','first_name','last_name','social_id','picture')
        extra_kwargs={
            'social_id':{'required':False},
            'picture':{'required':False}
        }
    
    def validate(self,attrs):
        email = attrs.get('email').lower()
        password= attrs.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                attrs['user']=user
            raise serializers.ValidationError("Incorrect Password")
        except User.DoesNotExist:
            pass
        return attrs

    def create(self, validated_data):
        user = validated_data.pop('user')
        if user:
            return user
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True,required=True)

    def validate_email(self,email):
        email = email.lower()
        return email

class GoogleOAuthSerializer(serializers.Serializer):
    id_token=serializers.CharField(required=True)