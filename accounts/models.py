from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from simple_history.models import HistoricalRecords
from django.contrib.auth.base_user import BaseUserManager


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "USER", "User"
    SUPERADMIN = "SUPERADMIN", "Superadmin"


class CustomUserManager(BaseUserManager):
    def create_user(self, telegram_id, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError('The Telegram ID must be set')
        user = self.model(telegram_id=telegram_id, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.SUPERADMIN)
        return self.create_user(telegram_id, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(null=True, blank=True, max_length=255)
    telegram_id = models.BigIntegerField(
        null=True, blank=True, unique=True, db_index=True
    )
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    telegram_link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=255, null=True, blank=True, choices=Role.choices, default=Role.USER
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    history = HistoricalRecords()

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def get_full_name(self):
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.last_name:
            name_parts.append(self.last_name)
        if self.username:
            name_parts.append(f"({self.username})")

        return " ".join(name_parts) if name_parts else None

    def __str__(self):
        return str(self.telegram_id)

    def get_short_name(self):
        return self.first_name or self.username or str(self.telegram_id)

    def save(self, *args, **kwargs):
        self.is_staff = self.role in [Role.ADMIN, Role.SUPERADMIN]
        
        link = []
        if self.username:
            link.append(f"https://t.me/{self.username}")
        if self.phone_number:
            link.append(f"https://t.me/{self.phone_number}")
        if self.telegram_id:
            link.append(f"https://t.me/{self.telegram_id}")
        if link:
            self.telegram_link = "\n".join(link)
            
        super().save(*args, **kwargs)
