from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import Subscribe, User

from .models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCartList, Tag)


class UserAdmin(BaseUserAdmin):
    """Админка юзера."""
    list_display = (
        'username',
        'email',
        'password',
        'first_name',
        'last_name',
    )
    list_display_links = (
        'username',
        'email',
    )
    list_editable = ('password', )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
    )
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = (
        'user',
        'author'
    )
    list_editable = (
        'author',
    )
    list_display_links = (
        'user',
    )
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name', )
    search_fields = ('name', )



class TagAdmin(admin.ModelAdmin):
    """Админка тэгов."""
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_editable = (
        'color',
        'slug'
    )
    list_display_links = (
        'name',
    )
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'



class RecipeAdmin(admin.ModelAdmin):
    """Админка рецетов."""
    list_display = (
        'name',
        'cooking_time',
        'text',
        'image',
        'author',
    )
    list_editable = (
        'cooking_time',
        'text',
        'image',
        'author',
    )
    list_display_links = (
        'name',
    )
    list_filter = ('name', )
    search_fields = ('name', 'author')
    empty_value_display = '-пусто-'


class RecipeIngredientsAdmin(admin.ModelAdmin):
    """Админка тэгов."""
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe', )
    empty_value_display = '-пусто-'


class ShoppingCartListAdmin(admin.ModelAdmin):
    """Админка тэгов."""
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe', )
    empty_value_display = '-пусто-'


class FavouriteAdmin(admin.ModelAdmin):
    """Админка тэгов."""
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe', 'user')
    empty_value_display = '-пусто-'

admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(ShoppingCartList, ShoppingCartListAdmin)
admin.site.register(Favourite, FavouriteAdmin)