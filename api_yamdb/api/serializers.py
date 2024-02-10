from django.conf import settings
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

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


class SignUpSerializer(serializers.ModelSerializer):
    """Следит за уникальностью полей email и username,
       валидирует username"""
    email = serializers.EmailField(
        max_length=254, required=True)

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                "Имя 'me' для username запрещено."
            )
        return username

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()
        if user_exists:
            user = User.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError(
                    {"username": "Неверно указан email пользователя"},
                    status.HTTP_400_BAD_REQUEST,
                )
        if email_exists:
            user = User.objects.get(email=email)
            if user.username != username:
                raise serializers.ValidationError(
                    {"email": "Пользователь с таким email уже существует"},
                    status.HTTP_400_BAD_REQUEST,
                )
        return data

# class SignUpSerializer(serializers.ModelSerializer):
#     """Сериализация создания пользователя."""
#
#     username = serializers.RegexField(
#         regex=r'^[\w.@+-]+\Z$',
#         max_length=settings.USERNAME_MAX_LENGTH,
#         required=True,
#     )
#     email = serializers.EmailField(
#         max_length=settings.FIELD_NAME_LENGTH,
#         required=True,
#     )
#
#     class Meta:
#         model = User
#         fields = ('username',
#                   'email',
#                   )
#
#     def validate_username(self, data):
#         """Запрещает пользователям присваивать себе имя me
#         и использовать повторные username и email."""
#         if data.get('username') == 'me':
#             raise serializers.ValidationError(
#                 'Использовать имя me запрещено'
#             )
#         # if User.objects.filter(username=data.get('username')):
#         #     raise serializers.ValidationError(
#         #         'Пользователь с таким username уже существует'
#         #     )
#         # if User.objects.filter(email=data.get('email')):
#         #     raise serializers.ValidationError(
#         #         'Пользователь с таким email уже существует'
#         #     )
#         return data


class UsersSerializer(serializers.ModelSerializer):
    """Сериализация пользователей."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=settings.FIELD_NAME_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
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

    def validate(self, data):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email."""
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


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

    def validate(self, data):
        if self.context['request'].method == 'POST' and Review.objects.filter(
                author=self.context['request'].user,
                title_id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError(
                'Нельзя оставить два отзыва на одно произведение.')
        return data


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
