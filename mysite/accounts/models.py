from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from mysite import settings


class UserManager(BaseUserManager):
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


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    patronymic = models.CharField(max_length=30, blank=True)  # По батькові
    gender = models.CharField(max_length=10, blank=True)  # Стать
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True)
    visit_reason = models.TextField(blank=True)  # Причина візиту
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def email_user(self, subject, message, from_email=None, **kwargs):
          send_mail(subject, message, from_email or settings.DEFAULT_FROM_EMAIL, [self.email], **kwargs)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_user
