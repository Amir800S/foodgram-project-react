from http import HTTPStatus

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .pdf_download import pdf_download
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from users.pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavouriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    UserSerializer,
)
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCartList,
    Tag,
)
from users.models import Subscribe, User


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тэгов только для просмотра."""

    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all().select_related(
        'author'
    ).prefetch_related(
        'tags',
        'ingredients'
    )
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = (
        "delete",
        "post",
        "get",
        "create",
        "patch",
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def favorite_shopping_cart(serializers, request, pk):
        context = {'request': request}
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart(
            FavouriteSerializer,
            request,
            pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favourite,
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart(
            ShoppingCartSerializer,
            request,
            pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCartList,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_recipe__user=request.user
            )
            .values("ingredient")
            .annotate(total_amount=Sum("amount")).order_by(
                'ingredient__name'
            )
            .values_list(
                "ingredient__name",
                "total_amount",
                "ingredient__measurement_unit"
            )
        )
        return pdf_download(ingredients)

class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = request.user
        queryset = user.follower.all()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = SubscriptionSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=(
            "post",
            "delete",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Функция подписки и отписки."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        obj = Subscribe.objects.filter(user=user, author=author)

        if request.method == "POST":
            if user == author:
                return Response('На себя подписаться нельзя',
                                status=HTTPStatus.BAD_REQUEST)
            if obj.exists():
                return Response(f'Вы уже подписаны на {author.username}',
                                status=HTTPStatus.BAD_REQUEST)
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=user, author=author),
                context={"request": request},
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if user == author:
            return Response('Вы не можете отписаться от самого себя',
                            status=HTTPStatus.BAD_REQUEST)
        if obj.exists():
            obj.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            f'Вы уже отписались от {author.username}',
            status=HTTPStatus.BAD_REQUEST
        )

    @action(detail=False, methods=("get",))
    def me(self, request):
        """Информация о пользователе."""
        user = request.user
        data = {
            "email": user.email,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_subscribed": False,
        }
        return Response(data)