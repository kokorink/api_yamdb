"""Описание модели пользователя сервиса."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_slug
from django.db import models

MODERATOR = 'moderator'
ADMIN = 'admin'
USER = 'user'

ROLE_CHOICES = (
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
    (USER, 'Пользователь'),
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=(validate_slug,),
        unique=True
    )
    email = models.EmailField(
        'Эл.почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True
    )
    role = models.CharField(
        'Роль',
        default=USER,
        max_length=settings.USERNAME_MAX_LENGTH,
        choices=ROLE_CHOICES,
    )
    bio = models.TextField(
        'О себе',
        blank=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USERNAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USERNAME_MAX_LENGTH,
        blank=True,
    )

    USERNAME_FIELD = 'username'

    @property
    def is_user(self):
        """Проверка соответствия роли 'Пользователь'."""

        return self.role == USER

    @property
    def is_admin(self):
        """Проверка соответствия роли 'Администратор'."""

        return (self.role == ADMIN
                or self.is_superuser
                )

    @property
    def is_moderator(self):
        """Проверка соответствия роли 'Модератор'."""

        return self.role == MODERATOR

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_user'
            )]

    def str(self):
        return self.username
