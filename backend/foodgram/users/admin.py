from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "recipes_count",
        "followers_count"
    )
    list_display_links = (
        "username",
        "email",
    )
    list_filter = ("username", "email")
    search_fields = ("username",)
    empty_value_display = "-пусто-"

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def followers_count(self, obj):
        return obj.author.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ("user", "author")
    list_editable = ("author",)
    list_display_links = ("user",)
    empty_value_display = "-пусто-"
