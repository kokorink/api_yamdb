"""Представление моделей в админ-зоне."""

from django.contrib import admin

from .models import User, Comment, Category, Title, Review, GenreTitle, Genre


class UserAdmin(admin.ModelAdmin):
    """Представление модели User."""

    list_display = ('id',
                    'username',
                    'email',
                    'role',
                    'bio',
                    'first_name',
                    'last_name'
                    )
    list_editable = ('role',
                     )
    search_fields = ('username', 'first_name', 'last_name',)
    list_display_links = ('username',)


class CategoryAdmin(admin.ModelAdmin):
    """Представление модели Category."""
    list_display = ('id',
                    'name',
                    'slug',
                    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class GenreAdmin(admin.ModelAdmin):
    """Представление модели Genre."""

    list_display = ('id',
                    'name',
                    'slug',
                    )
    list_editable = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class TitleAdmin(admin.ModelAdmin):
    """Представление модели Title."""

    list_display = ('id',
                    'name',
                    'year',
                    'category',
                    )
    list_editable = ('category',
                     )
    search_fields = ('name', 'year')
    list_filter = ('category',)
    list_display_links = ('name',)


class GenreTitleAdmin(admin.ModelAdmin):
    """Представление связки моделей Genre и Title."""

    list_display = ('id',
                    'title_id',
                    'genre_id',
                    )
    list_editable = ('genre_id',
                     )
    search_fields = ('title_id',)
    list_filter = ('genre_id', )
    list_display_links = ('id',)


class ReviewAdmin(admin.ModelAdmin):
    """Представление модели Review."""

    list_display = ('id',
                    'text',
                    'author',
                    'score',
                    'pub_date'
                    )
    list_editable = ('text',)
    search_fields = ('pub_date', 'score', 'author')
    list_filter = ('author', 'score')
    list_display_links = ('id',)


class CommentAdmin(admin.ModelAdmin):
    """Представление модели Comment."""

    class ReviewAdmin(admin.ModelAdmin):
        """Представление модели Review."""

        list_display = ('id',
                        'review_id',
                        'text',
                        'author',
                        'pub_date'
                        )
        list_editable = ('author',)
        search_fields = ('review_id', 'review_id', 'author')
        list_filter = ('review_id', 'review_id')
        list_display_links = ('id',)


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(GenreTitle, GenreTitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
