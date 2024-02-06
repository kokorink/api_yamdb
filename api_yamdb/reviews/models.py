"""Описание моделей приложения reviews."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

from users.models import User


class NameSlugModel(models.Model):
    """Базовая модель для моделей содержащих поля Name и Slug."""

    name = models.CharField(
        max_length=settings.FIELD_NAME_LENGTH,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        unique=True, db_index=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.MAX_NAME_LENGTH]


class ReviewCommentModel(models.Model):
    """Базовая модель для моделей Review и Comment."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Дата публикации'
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
        max_length=settings.FIELD_NAME_LENGTH,
        db_index=True,
        verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        validators=(validate_year,),
        verbose_name='Год'
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
        null=True,
        blank=True,
        verbose_name='Описание'
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
        validators=[
            MinValueValidator(1, message="Оценка не может быть меньше 1"),
            MaxValueValidator(10, message="Оценка не может быть больше 10")
        ],
        verbose_name='Оценка'
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
