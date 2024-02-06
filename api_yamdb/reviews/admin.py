"""Представление моделей в админ-зоне."""

from django.contrib import admin

from .models import Category, Comments, Genre, Review, Title


class CategoryGenreAdmin(admin.ModelAdmin):
    """Представление модели Category."""
    list_display = ('id',
                    'name',
                    'slug',
                    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class CommentAdmin(admin.ModelAdmin):
    """Представление модели Comment."""

    list_display = ('id',
                    'author',
                    'text',
                    'pub_date')
    list_editable = ('text',)
    search_fields = ('pub_date', 'author')
    list_filter = ('author',)
    list_display_links = ('id',)


class TitleAdmin(admin.ModelAdmin):
    """Представление модели Title."""

    list_display = ('id',
                    'name',
                    'year',
                    'category',
                    'description',
                    )
    filter_horizontal = ('genre',)
    list_editable = ('category', 'description')
    search_fields = ('name', 'year')
    list_filter = ('category',)
    list_display_links = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    """Представление модели Review."""
    list_display = ('id',
                    'author',
                    'text',
                    'pub_date',
                    'score',
                    'title')
    search_fields = ('pub_date', 'score', 'author')
    list_filter = ('author', 'score', 'title')
    list_display_links = ('id',)


admin.site.register(Category, CategoryGenreAdmin)
admin.site.register(Genre, CategoryGenreAdmin)
admin.site.register(Comments, CommentAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
