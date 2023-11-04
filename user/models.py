from djongo import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid 
from datetime import datetime
    
# Create your models here.

   


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verified_dateTime = models.DateTimeField(null=True)
    email_verify_token = models.CharField(max_length=20, null=True)
    email_verify_token_dateTime = models.DateTimeField(null=True)
    forgot_password_token = models.CharField(max_length=20, null=True)
    forgot_password_token_dateTime = models.DateTimeField(null=True)
    is_locked = models.BooleanField(default=False)
    locked_dateTime = models.DateTimeField(null=True)
    logged_in_tokens = models.JSONField(default=list) 
    profile = models.JSONField(default=dict)
    connected_user_ids = models.JSONField(default=list)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_formatted_data(self):
        formatted_data = {
            '_id': self._id,
            'name': self.name,
            'email': self.email,
            'country': self.country,
            'city': self.city,
            'profile_pic': self.profile.get('profile_picture'),
        }
        return formatted_data

    def get_user_data(self):
        formatted_data = {
            '_id': self._id,
            'name': self.name,
            'email': self.email,
            'country': self.country,
            'city': self.city,
            'profile_pic': self.profile.get('profile_picture'),
            'cover_pic': self.profile.get('cover_picture'),
            'dob': self.profile.get('dob'),
            'bio': self.profile.get('bio'),
            'social_media_links': self.profile.get('social_media_links')
        }
        
        return formatted_data



 