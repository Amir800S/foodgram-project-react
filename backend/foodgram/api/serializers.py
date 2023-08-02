import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favourite, Ingredient,
                            RecipeIngredients, Recipe,
                            Tag, ShoppingCartList)
from users.models import User, Subscribe



class UserSerializer(serializers.ModelSerializer):
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

class UserCreationSerializer(serializers.ModelSerializer):
    """Создание пользователей."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

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


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер подписок пользователя."""
    is_subscribed = SerializerMethodField()
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name'
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(user=user, author=obj).exists()
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        return obj.recipes.all()

class Base64ImageField(serializers.Field):
    """Сериалайзер картинок."""
    def to_internal_value(self, data):
        if not isinstance(data, str) or not data.startswith('data:image'):
            raise serializers.ValidationError(
                'Неправильный формат изображения.'
            )
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        return super().to_internal_value(data)
    def to_representation(self, value):
        return value.url


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
        fields = '__all__'

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

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            Recipe.objects.create(**validated_data)
        )
        return recipe

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance