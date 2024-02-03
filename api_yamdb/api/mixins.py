from rest_framework import mixins, filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination

from .permissions import IsAdminUserOrReadOnly


class ModelMixinSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    filter_backends = [filters.SearchFilter, ]
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    search_fields = ('name',)
    permission_classes = (IsAdminUserOrReadOnly,)
