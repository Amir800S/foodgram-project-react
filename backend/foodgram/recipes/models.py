from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from recipes import constants
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        "Название ингредиента", max_length=constants.INGREDIENT_NAME, null=False
    )
    measurement_unit = models.CharField(
        "Единица для измерения", max_length=constants.INGREDIENT_UNIT
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        "Название тэга", unique=True, max_length=constants.TAG_NAME
    )
    color = models.CharField(
        "Цветовой HEX-код", null=True, max_length=constants.TAG_COLOR
    )
    slug = models.SlugField("Слаг", unique=True, max_length=constants.TAG_SLUG)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Автор",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингредиенты",
        through='RecipeIngredients'
    )
    text = models.TextField(
        "О рецепте",
    )
    image = models.ImageField(
        "Изображение рецепта", upload_to="recipes/"
    )
    name = models.CharField(
        "Название рецепта", max_length=constants.RECIPE_NAME
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Тэги"
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Favourite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favourites_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            UniqueConstraint(fields=["user", "recipe"], name="favourites")
        ]

    def __str__(self):
        return "{} В Избранном у {}".format(self.recipe, self.user)


class RecipeIngredients(models.Model):
    """Модель ингредиентов в рецептах"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингредиента",
        validators=[MinValueValidator(constants.INGREDIENT_MIN_AMOUNT)],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return (
            f"В рецепте {self.recipe},"
            f" {self.ingredient} содержится" f"{self.amount}."
        )


class ShoppingCartList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart_user",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'