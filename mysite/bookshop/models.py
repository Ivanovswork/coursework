from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


COMPANIES_CHOIСES = [
    ('self-publishing', 'Самиздат'),
    ('publishing house', 'Издательство'),
]


class Companies(models.Model):
    name = models.CharField(verbose_name='Название', max_length=40, blank=False)
    status = models.CharField(verbose_name='Статус', choices=COMPANIES_CHOIСES, blank=False)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email), password=password, **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(verbose_name="e-mail", null=False, unique=True)
    name_validator = UnicodeUsernameValidator()
    name = models.CharField(
        verbose_name="Имя", max_length=80, validators=[name_validator], blank=True
    )
    company = models.ForeignKey(
        Companies, verbose_name="Компания", related_name="worker", blank=True, null=True, on_delete=models.CASCADE
    )
    is_active = models.BooleanField(verbose_name="Аккаунт активирован", default=False)
    is_staff = models.BooleanField(verbose_name="Аккаунт уполномоченного лица", default=False)
    is_superuser = models.BooleanField(verbose_name="Аккаунт администратора", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"

    def __str__(self):
        return f"{self.email} {self.name}"
