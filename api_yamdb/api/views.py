from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
    IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .mixins import ModelMixinSet
from .permissions import (IsAdminPermission, IsAdminUserOrReadOnly,
                          IsAuthorAdminSuperuserOrReadOnlyPermission)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TokenSerializer, TitleReadSerializer,
    TitleWriteSerializer, UserCreateSerializer, UsersSerializer,
    NewUserCreateSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class SignUpView(APIView):
    """
    POST-запрос с email и username генерирует
    письмо с кодом для получения токена.
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = NewUserCreateSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        """Создание пользователя И Отправка письма с кодом."""
        serializer = NewUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                **serializer.validated_data)
        except IntegrityError:
            return Response(
                'Такой логин или email уже существуют',
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmation_code = default_token_generator.make_token(user)
        user.save()

        send_mail('Код подтверждения',
                  f'Ваш код подтверждения: {confirmation_code}',
                  [settings.AUTH_EMAIL,],
                  (user.email,),
                  fail_silently=False,
                  )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (
        # IsAdminPermission,
        permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = LimitOffsetPagination

    @action(methods=['GET', 'PATCH'],
            url_path='me',
            url_name='me',
            permission_classes=(IsAuthenticated,),
            detail=False)
    def about_me(self, request):
        if request.method == 'PATCH':
            serializer = UserCreateSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserCreateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """
    POST-запрос с username и confirmation_code
    возвращает JWT-токен.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError('Неверный код')
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class CategoryViewSet(ModelMixinSet):
    """Получить список всех категорий без токена."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ModelMixinSet):
    """Получить список всех жанров без токена."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех объектов без токена."""

    permission_classes = (IsAdminUserOrReadOnly,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('-rating')
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorAdminSuperuserOrReadOnlyPermission,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorAdminSuperuserOrReadOnlyPermission,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
