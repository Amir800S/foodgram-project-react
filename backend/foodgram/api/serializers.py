from http import HTTPStatus

from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes import constants
from users.models import Subscribe, User
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCartList,
    Tag,
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
        request = self.context.get("request")
        return (request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""

    image = Base64ImageField(read_only=True)

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
            "author",
            "id",
            "user",
        )

    def validate(self, data):
        user = data.get("user")
        author = data.get("author")

        if Subscribe.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                "Вы уже подписаны на этого автора"
            )
        if user == author:
            raise ValidationError(
                "Подписаться на самого себя невозможно",
                code=HTTPStatus.BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["author"] = SubscriptionSerializer(instance.author).data
        return representation

class SubscriptionSerializer(UserSerializer):
    """Сериалайзер для подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="author.recipes.count")

    class Meta:
        model = User
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

    def get_recipes(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        recipe_obj = obj.recipes.all()
        limit = self.context.get("request").GET.get("recipes_limit")
        if limit:
            try:
                recipe_obj = recipe_obj[:int(limit)]
            except ValueError:
                pass
        return RecipeSerializer(
            recipe_obj, many=True, context={"request": request}).data


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для избранного."""

    class Meta:
        model = Favourite
        fields = (
            "user",
            "recipe"
        )

    def validate(self, data):
        if self.Meta.model.objects.filter(
                user=data.get("user"), recipe=data.get("recipe")
        ).exists():
            raise serializers.ValidationError({
                "errors": 'Рецепт уже есть в избранном.'})
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
        request = self.context.get("request")
        return (request.user.is_authenticated
                and obj.shopping_recipe.filter(user=request.user).exists())

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (request.user.is_authenticated
                and obj.favourites_recipe.filter(user=request.user).exists())


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=constants.INGREDIENT_MIN_AMOUNT,
        max_value=constants.INGREDIENT_MAX_AMOUNT,
        error_messages={
            "min_value": "Не может быть меньше 1.",
            "max_value": "Это слишком много."
        }
    )

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
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=constants.INGREDIENT_MIN_AMOUNT,
        max_value=constants.INGREDIENT_MAX_AMOUNT
    )

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

    def validate(self, data):
        tags = data.get("tags")
        ingredients = data.get("ingredients")
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"tags": "Теги должна быть уникальными."}
            )
        ingredient_list = {ingredient["id"] for ingredient in ingredients}
        if len(ingredient_list) != len(ingredients):
            raise serializers.ValidationError(
                {'ingredients':"Ингредиенты не должны повторяться."}
            )
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нужен хотя бы один тег"}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хотя бы один ингредиент"}
            )
        return data

    def validate_image(self, image):
        supported_formats = ["jpg", "jpeg", "png"]
        file_extension = image.name.split('.')[-1]
        if not image:
            raise serializers.ValidationError(
                {'image' :"Нужна картинка."}
            )
        if file_extension.lower() not in supported_formats:
            raise serializers.ValidationError(
                {'file_extension':"Непонятный формат картинки."}
            )
        return image

    @staticmethod
    def create_ingredients_and_tags(recipe, tags, ingredients):
        recipe.tags.set(tags)
        ingredients_data = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredients_data)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context.get("request").user,
            **validated_data
        )
        self.create_ingredients_and_tags(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        self.create_ingredients_and_tags(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShoppingCartSerializer(FavouriteSerializer):
    """Сериализатор добавления рецепта в корзину"""

    class Meta(FavouriteSerializer.Meta):
        model = ShoppingCartList

    def validate(self, data):
        recipe = self.instance
        user = self.context.get("request").user
        if self.Meta.model.objects.filter(
                recipe=recipe, user=user
        ).exists():
            raise serializers.ValidationError(
                detail="Рецепт уже добавлен в корзину",
                code=HTTPStatus.BAD_REQUEST,
            )
        return data
