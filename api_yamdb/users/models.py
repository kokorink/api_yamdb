from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.validators import validate_slug
from django.db import models

ROLE_CHOICES = (
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('user', 'Пользователь'),
)


class User(AbstractBaseUser):
    """Модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=(validate_slug,)
    )
    email = models.EmailField(
        'Эл.почта',
        max_length=settings.EMAIL_MAX_LENGTH
    )
    role = models.CharField(
        'Роль',
        default='user',
        max_length=settings.USERNAME_MAX_LENGTH,
    )
    bio = models.TextField(
        'О себе',
        null=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USERNAME_MAX_LENGTH,
        null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USERNAME_MAX_LENGTH,
        null=True
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='314159265358979'
    )

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email',),
                name='unique_user'
            )]
        ordering = ('-id',)

    def str(self):
        return self.username