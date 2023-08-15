import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favourite, Ingredient,
                            RecipeIngredients, Recipe,
                            Tag, ShoppingCartList)
from users.models import User, Subscribe



class UserCreateSerializer(serializers.ModelSerializer):
    """Получение списка пользователей."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(user=user, author=obj).exists()


class PasswordChangeSerializer(serializers.Serializer):
    """Сериалайзер для смены пароля."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    def validate(self, data):
        user = self.context['request'].user
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Пароли не совпадают!'
            )
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError('Старый пароль неверный!')
        return data
    def update(self, instance, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data['new_password'])
        user.save()
        return user

class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер подписок пользователя."""
    is_subscribed = SerializerMethodField()
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    email = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
    def get_recipes(self, obj):
        return obj.recipes.all()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return Subscribe.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тэга."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента."""
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты для рецепта."""
    class Meta:
        model = RecipeIngredients
        fields = '__all__'

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка рецептов."""
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favourited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            ShoppingCartList.objects.filter(
                user=self.context['request'].user,recipe=obj
            ).exists()
        )

    def get_is_favourited(self, obj):
        return (
            Favourite.objects.filter(
                user=self.context['request'].user,recipe=obj
            ).exists()
        )

class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount',
        )

class UserReadSerializer(UserSerializer):
    """Сериалайзер для чтения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(
            user=user, author=obj
        ).exists()
class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание, изменение и удаление рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserReadSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate(self, obj):
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Укажите минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно минимум 1 ингредиент.'
            )
        return obj

    def create_ingredients_and_tags(self, recipe, tags, ingredients):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients_and_tags(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        return self.create_ingredients_and_tags(
            tags, ingredients, instance
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context=self.context
        ).data