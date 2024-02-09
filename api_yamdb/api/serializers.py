from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers
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
    """Сериализация создания пользователя."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True
    )
    email = serializers.EmailField(
        max_length=settings.FIELD_NAME_LENGTH,
        required=True,
    )

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  )
        # lookup_field = 'username'
        # extra_kwargs = {
        #     'username': {'required': True},
        #     'email': {'required': True}
        # }

    def validate(self, data):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email."""
        if data.get('username') != 'me' or User.objects.filter(username=data.get('username')):
            return data
        raise serializers.ValidationError(
            'Использовать имя me запрещено'
        )





    # def validate(self, attrs):
    #     if User.objects.filter(email=attrs.get('email')):
    #         user = User.objects.get(email=attrs.get('email'))
    #         if user.username != attrs.get('email'):
    #             raise serializers.ValidationError(
    #                 'Данный Email уже используется'
    #             )
    #     if User.objects.filter(username=attrs.get('username')):
    #         user = User.objects.get(username=attrs.get('username'))
    #         if user.username != attrs.get('username'):
    #             raise serializers.ValidationError(
    #                 'Данный Username уже используется'
    #             )
    #     return super().validate(attrs)


    # def validate_username(self, data):
    #     if User.objects.filter(username=data.get('username')):
    #         raise serializers.ValidationError(
    #             'Нельзя username'
    #         )
    #     return data

    # def validate_email(self, data):
    #     if data.get('email') == self.username:
    #         raise serializers.ValidationError(
    #             'Нельзя email'
    #         )
    #     return data
        # if User.objects.filter(username=data.get('username')):
        #     raise serializers.ValidationError(
        #         'Пользователь с таким username уже существует'
        #     )
        # if User.objects.filter(email=data.get('email')):
        #     raise serializers.ValidationError(
        #         'Пользователь с таким email уже существует'
        #     )
        # return data


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
