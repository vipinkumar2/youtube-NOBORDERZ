from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import JSONField

# Create your models here.


class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """Helps Django work with our custom user model."""

    def create_user(
        self,
        email,
        timezone="Asia/Kolkata",
        username=None,
        password=None,
        user_language="en",
    ):
        """Creates a new user profile object."""

        if not email:
            raise ValueError("Users must have an email address.")
        if not username:
            username = email
        if not password:
            raise ValueError("Users must have an password.")
        if not user_language:
            raise ValueError("Users must have an language.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            timezone=timezone,
            user_language=user_language,
        )

        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        """Creates and saves a new superuser with given details."""

        user = self.create_user(email=email, username=username, password=password)

        user.is_staff = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    """To Store user basic information"""

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("ja", "Japanese"),
        ("ko", "Korean"),
        ("zh-hans", "Chinese"),
    )

    USER_TYPES = (
        ("marketing_team", "marketing_team"),
        ("tester", "tester"),
        ("user", "user"),
    )

    APP_CHOICES = (
        ('IG', 'IG'),  # Instagram
        ('TT', 'TT'),  # TikTok
        ('YT', 'YT'),  # YouTube
        ('TW', 'TW'),  # Twitter
        ('TL', 'TL')  # Telegram
    )
    
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email_verified = models.BooleanField(default=False)
    app_choice = models.CharField(max_length=200, choices=APP_CHOICES, default="IG")
    user_type = models.CharField(max_length=200, choices=USER_TYPES, default="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    timezone = models.CharField(max_length=100, blank=True, null=True, default=None)
    user_language = models.CharField(
        default="en", choices=LANGUAGE_CHOICES, max_length=15
    )
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]

    def __str__(self):
        return self.username


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    generated_otp = models.CharField(max_length=6, default="000000")
    email = models.EmailField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.generated_otp)
