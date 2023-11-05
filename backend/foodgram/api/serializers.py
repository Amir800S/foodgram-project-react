from http import HTTPStatus

from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.conf import settings

from users.models import Subscribe, User
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCartList,
    Tag,
)

class UserCreationSerializer(UserCreateSerializer):
    """Создание пользователей."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и получение списка пользователей."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())



class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    id = serializers.ReadOnlyField(source="author.id")
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    # БЕЗ ЭТИХ ПОЛЕЙ НЕ РАБОТАЕТ

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )

class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода подписок пользователя."""

    class Meta:
        model = Subscribe
        fields = (
            'author',
            'id',
        )

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')

        if Subscribe.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                "Вы уже подписаны на этого автора")
        if user == author:
            raise ValidationError(
                "Подписаться на самого себя невозможно",
                code=HTTPStatus.BAD_REQUEST,
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписки."""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="author.recipes.count")
    is_subscribed = serializers.SerializerMethodField()
    # БЕЗ ЭТИХ ПОЛЕЙ НЕ РАБОТАЕТ

    class Meta:
        model = Subscribe
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return Subscribe.objects.filter(author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe_obj = obj.author.recipes.all()
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                raise serializers.ValidationError(
                    {'recipes_limit': 'Тип должен быть int.'}
                )
            recipe_obj = recipe_obj[:int(limit)]
        return RecipeSerializer(
            recipe_obj, many=True, context={'request': request}).data


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для избранного."""

    class Meta:
        model = Favourite
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        if Favourite.objects.filter(
                user=data.get('user'), recipe=data.get('recipe')
        ).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже есть в избранном.'})
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context=self.context,
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тэга."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиента."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты для рецепта."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для списка рецептов."""

    author = UserCreateSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.shopping_recipe.filter(user=request.user).exists())

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.favourites_recipe.filter(user=request.user).exists())

class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""

    id = serializers.IntegerField()
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredient.objects.all()
    # )
    # amount = serializers.IntegerField(
    #     min_value=settings.INGREDIENT_MIN_AMOUNT,
    #     max_value=settings.INGREDIENT_MAX_AMOUNT
    # )

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "amount",
        )



class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание, изменение и удаление рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserCreateSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate(self, obj):
        if not obj.get("tags"):
            raise serializers.ValidationError("Укажите минимум 1 тег.")
        if not obj.get("ingredients"):
            raise serializers.ValidationError("Нужно минимум 1 ингредиент.")
        return obj

    def create_ingredients_and_tags(self, recipe, tags, ingredients):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
                recipe=recipe,
            )
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients_and_tags(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance = super().update(instance, validated_data)
        return self.create_ingredients_and_tags(instance, tags, ingredients)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShoppingCartSerializer(RecipeSerializer):
    """Сериализатор добавления рецепта в корзину"""

    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        recipe = self.instance
        user = self.context.get("request").user
        if ShoppingCartList.objects.filter(
                recipe=recipe, user=user
        ).exists():
            raise serializers.ValidationError(
                detail="Рецепт уже добавлен в корзину",
                code=HTTPStatus.BAD_REQUEST,
            )
        return data