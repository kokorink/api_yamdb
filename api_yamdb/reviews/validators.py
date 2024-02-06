"""Валидаторы приложения 'reviews'."""

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверка года выпуска произведения."""

    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'{value} не может быть больше {now}'
        )
