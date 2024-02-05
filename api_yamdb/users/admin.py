"""Представление моделей в админ-зоне."""

from django.contrib import admin

from .models import User


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


admin.site.register(User, UserAdmin)