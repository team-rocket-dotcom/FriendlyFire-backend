from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models, transaction
from decouple import config
import uuid

from wallet.models import Wallet
# Create your models here.

AUTH_PROVIDERS = (
    ('email','Email'),
    ('google','Google'),
    ('github','Github'),
    ('twitter','Twitter')
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, auth_provider='email', password=None, *args, **kwargs):
        if not email:
            raise ValueError("email is required")

        email = self.normalize_email(email)
        if auth_provider=='email':
            kwargs['social_id']=email
            user = self.model(email=email, auth_provider=auth_provider, *args, **kwargs)

            if not password:
                raise ValueError('Password is required for email sign-in')

            user.set_password(password)

        elif auth_provider=='google':
            user = self.model(email=email,auth_provider= auth_provider, *args, **kwargs)
            user.set_unusable_password()

        else:
            raise ValueError('Invalid auth provider')

        user.save()
        return user

    def create_user_with_wallet(self, email, auth_provider='email', password=None, *args, **kwargs):
        with transaction.atomic():
            user = self.create_user(email=email, auth_provider=auth_provider, password=password, *args, **kwargs)
            Wallet.objects.create(owner=user,balance=0.00,currency='inr')
            return user
        return None

class CustomUser(AbstractBaseUser, PermissionsMixin):

    id = models.CharField(max_length=50, unique=True, primary_key=True)
    social_id = models.CharField(max_length=25, unique=True)

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    picture = models.URLField(default=config('USER_PFP'))

    auth_provider = models.CharField(
        max_length= 20,
        choices= AUTH_PROVIDERS,
        default='email'
    )

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name', 'last_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f'{uuid.uuid4().hex.lower()}'
        self.full_clean() #forces validation(the auth_provider field will have no value other than the CHOICES)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.email} ({self.first_name} {self.last_name}, {self.auth_provider})'