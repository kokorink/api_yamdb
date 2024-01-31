"""Описание моделей проекта."""
from django.core.validators import (validate_slug,
                                    MinValueValidator,
                                    MaxValueValidator)
from django.db import models

TEXT_LENGTH = 500
TITLE_NAME_LENGTH = 20
SLUG_MAIL_LENGTH = 50
STR_TEXT_LENGTH = 50
MIN_SCORE = 1
MAX_SCORE = 10


class User(models.Model):
    """Модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=TITLE_NAME_LENGTH,
        validators=(validate_slug,)
    )
    email = models.EmailField(
        'Эл.почта',
        max_length=SLUG_MAIL_LENGTH
    )
    role = models.CharField(
        'Роль',
        max_length=TITLE_NAME_LENGTH,
        default='user'
    )
    bio = models.TextField(
        'О себе',
        max_length=TEXT_LENGTH,
        null=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=SLUG_MAIL_LENGTH,
        null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=SLUG_MAIL_LENGTH,
        null=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email',),
                name='unique_user'
            )]
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(
        'Название',
        max_length=TITLE_NAME_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_MAIL_LENGTH,
        validators=(validate_slug,),
        unique=True
    )


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField(
        'Название',
        max_length=TITLE_NAME_LENGTH,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_MAIL_LENGTH,
        validators=(validate_slug,),
        unique=True
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'slug',),
                name='unique_genre'
            )]
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        'Название',
        max_length=TITLE_NAME_LENGTH)
    year = models.DateTimeField(
        verbose_name='Дата выхода'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='категория',
        related_name='category')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'category', 'year'),
                name='unique_title'
            )]
        ordering = ('-year',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель связи произведения с жанром."""

    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Идентификатор произведения',
    )
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Идентификатор жанра',
    )

    class Meta:
        verbose_name = 'произведение-жанр'
        verbose_name_plural = 'Произведения-жанры'
        constraints = [
            models.UniqueConstraint(
                fields=('title_id', 'genre_id',),
                name='unique_genre_title'
            )]
        ordering = ('-genre_id',)

    def __str__(self):
        return f'{self.title_id} - {self.genre_id}'


class Review(models.Model):
    """Модель отзыва."""

    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Название'
        )
    text = models.TextField(
        'Текст',
        max_length=TEXT_LENGTH
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.IntegerField(
        'Оценка',
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE),
        ),
        error_messages={'validators': 'Выберите оценку от 1 до 10'}

    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title_id', 'author', ),
                name='unique_review'
            )]
        ordering = ('-score',)

    def __str__(self):
        return self.text[:STR_TEXT_LENGTH]


class Comment(models.Model):
    """Модель комментария."""

    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(
        'Комментарий',
        max_length=TEXT_LENGTH
     )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
     )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True
     )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'review_id', ),
                name='unique_comment'
            )]
        ordering = ('review_id', '-pub_date')

    def __str__(self):
        return self.text[:TITLE_NAME_LENGTH]
