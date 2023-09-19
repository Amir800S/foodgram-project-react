from http import HTTPStatus

from django.db.models import Sum
from django.http import FileResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from io import BytesIO

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCartList, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavouriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          RecipeSerializer, RecipeIngredientSerializer, TagSerializer)
from .filters import RecipeFilter
from foodgram.settings import FILE_NAME


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
    filterset_class = RecipeFilter
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
        recipe = get_object_or_404(Recipe, pk=pk)

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
                return Response(
                    'Рецепта нет в избранном.',
                    status=status.HTTP_404_NOT_FOUND,
                )
            Favourite.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                'Рецепт успешно удалён из избранного.',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(('post', 'delete'),
            detail=True,
            permission_classes=(IsAuthenticated, ),
            )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCartList.objects.filter(user=request.user,
                                                recipe=recipe).exists():
                ShoppingCartList.objects.create(user=request.user, recipe=recipe)
                return Response(f'Рецепт добавлен в список покупок!',
                                status=status.HTTP_201_CREATED
                                )
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        if request.method == 'DELETE':
            get_object_or_404(ShoppingCartList, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,),
            )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        p.setFont('Arial', 12)
        p.drawString(100, 750, "Список покупок:")
        y = 730
        for ingredient in file_list:
            p.drawString(100, y, ingredient)
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="purchases.pdf"'
        return response
