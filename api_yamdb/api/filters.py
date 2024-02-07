from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Фильтрация произведений."""

    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='iexact'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='iexact'
    )

    class Meta:
        model = Title
        fields = '__all__'
