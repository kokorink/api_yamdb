"""Описание моделей приложения reviews."""

import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class NameSlugModel(models.Model):
    """Базовая модель для моделей содержащих поля Name и Slug."""

    name = models.CharField(
        'Имя',
        max_length=settings.FIELD_NAME_LENGTH,
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.MAX_NAME_LENGTH]


class ReviewCommentModel(models.Model):
    """Базовая модель для моделей Review и Comment."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.CharField(
        'Текст отзыва',
        max_length=settings.MAX_REVIEW_TEXT,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True, db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:settings.MAX_TEXT_LENGTH]


class Category(NameSlugModel):
    """Модель категорий."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Модель жанров."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(
        'Название',
        max_length=settings.FIELD_NAME_LENGTH,
        db_index=True,
    )
    year = models.SmallIntegerField(
        'Год',
        validators=[
            MinValueValidator(
                -4000,
                message="Согласно справочным данным, первые писания "
                        "датируются 4 тысячелетием до н.э. Введите, "
                        "пожалуйста, корректные данные."),
            MaxValueValidator(
                datetime.datetime.now().year,
                message="Год выпуска не может превышать текущий. Введите. "
                        "пожалуйста, корректные данные.")
        ],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    description = models.TextField(
        'Описание',
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(ReviewCommentModel):
    """Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Обзор'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(
                1,
                message="Оценка не может быть меньше 1"),
            MaxValueValidator(
                10,
                message="Оценка не может быть больше 10")
        ],
    )

    class Meta(ReviewCommentModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique review'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'


class Comments(ReviewCommentModel):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
