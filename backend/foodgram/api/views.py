from http import HTTPStatus

from django.http import HttpResponse
from rest_framework import status
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
                          RecipeReadSerializer,
                          RecipeSerializer,
                          FavouriteSerializer,)


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated, ),
            )
    def favourite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепт уже есть в избранном.',
                                status=status.HTTP_400_BAD_REQUEST,
                                )
            serializer = FavouriteSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепта нет в избранном.',
                                status=status.HTTP_404_NOT_FOUND,
                                )
            Favourite.objects.filter(user=user, recipe=recipe).delete()
            return Response('Рецепт успешно удалён из избранного.',
                            status=status.HTTP_204_NO_CONTENT
                            )

    @action(('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated, ),
            )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепт уже есть в списке.',
                                status=status.HTTP_400_BAD_REQUEST,
                                )
            serializer = FavouriteSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response('Рецепта нет в списке.',
                                status=status.HTTP_404_NOT_FOUND,
                                )
            Favourite.objects.filter(user=user, recipe=recipe).delete()
            return Response('Рецепт успешно удалён из списка.',
                            status=status.HTTP_204_NO_CONTENT
                            )
    @action(detail=False,
            methods=('get', ),
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_pdf(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        return response