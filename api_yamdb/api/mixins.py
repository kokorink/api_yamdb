from rest_framework import filters, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from .permissions import IsAdminUserOrReadOnly


class ModelMixinSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    filter_backends = [filters.SearchFilter, ]
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    search_fields = ('name',)
    permission_classes = (IsAdminUserOrReadOnly,)
