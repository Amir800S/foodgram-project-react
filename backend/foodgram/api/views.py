from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favourite, Ingredient, RecipeIngredients,
                            Recipe, ShoppingCartList, Tag)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeCreateSerializer,
                          RecipeReadSerializer,)


class IngredientViewSet(ModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тэгов только для просмотра."""
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    http_method_names = (
        'delete',
        'post',
        'get',
        'create',
        'patch',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            url_path='favourite',
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def post_or_delete_favourite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            serializer = RecipeCreateSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            if Favourite.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                return Response(
                    'Вы уже добавили этот рецепт!',
                    status=HTTPStatus.BAD_REQUEST
                )
            Favourite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Favourite, user=request.user,
                              recipe=recipe).delete()
            return Response('Рецепт удален!',
                            status=HTTPStatus.NO_CONTENT)

    @action(detail=True,
            methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def create_or_delete_shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            serializer = RecipeCreateSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            if ShoppingCartList.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCartList.objects.create(
                    user=request.user, recipe=recipe
                )
                return Response(
                    'Рецепт уже добавлен в список!',
                    status=HTTPStatus.BAD_REQUEST
                )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingCartList, user=request.user, recipe=recipe
            ).delete()
            return Response(
                'Рецепт удален!',
                status=HTTPStatus.NO_CONTENT
            )
    @action(detail=False,
            methods=('get', ),
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_pdf(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        return response