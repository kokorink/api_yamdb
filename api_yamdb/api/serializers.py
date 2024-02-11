from django.conf import settings
from rest_framework import serializers, status

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User


class TokenSerializer(serializers.Serializer):
    """Сериализация получения токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
    )
    email = serializers.EmailField(
        max_length=settings.FIELD_NAME_LENGTH,
        required=True,
    )

    @staticmethod
    def validate_username(username):
        """Проверка на запрет использования имени 'me'."""

        if username == 'me':
            raise serializers.ValidationError(
                "Имя 'me' для username запрещено."
            )
        return username

    def validate(self, attrs):
        """Запрет на использование занятых username и email."""

        username = attrs.get('username')
        email = attrs.get('email')
        if User.objects.filter(username=username).exists():
            if User.objects.get(username=username).email != email:
                raise serializers.ValidationError(
                    {"username": "Неверно указан email пользователя"},
                    status.HTTP_400_BAD_REQUEST,
                )
        if User.objects.filter(email=email).exists():
            if User.objects.get(email=email).username != username:
                raise serializers.ValidationError(
                    {"email": "Пользователь с таким email уже существует"},
                )
        return attrs


class SignUpSerializer(BaseUserSerializer):
    """Сериализация при регистрации / повторного запроса подтверждения."""

    class Meta:
        model = User
        fields = (
            'email',
            'username')

    def validate(self, attrs):
        """Валидация на запрет повторного использования username и email не
        соответствующих друг другу."""

        username = attrs.get('username')
        email = attrs.get('email')
        if (User.objects.filter(username=username).exists()
                and User.objects.filter(email=email).exists()):
            if User.objects.get(username=username).email != email:
                raise serializers.ValidationError(
                    {"username": "Имя пользователя не соответствует email.",
                     "email": "email не соответствует имени пользователя."},
                )

        return super().validate(attrs)


class UsersSerializer(BaseUserSerializer):
    """Сериализация пользователей."""

    first_name = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=False)
    last_name = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True, default=0.00)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'category',
            'description',
            'genre',
            'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        allow_empty=False
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'category',
            'description',
            'genre'
        )

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'author',
            'text',
            'pub_date',
            'score'
        )

    def validate(self, attrs):
        if self.context['request'].method == 'POST' and Review.objects.filter(
                author=self.context['request'].user,
                title_id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError(
                'Нельзя оставить два отзыва на одно произведение.')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comments
        fields = (
            'id',
            'author',
            'text',
            'pub_date'
        )
