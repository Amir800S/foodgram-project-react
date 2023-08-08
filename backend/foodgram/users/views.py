from http import HTTPStatus

from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from api.serializers import (SubscribeSerializer,
                             UserSerializer,
                             UserCreateSerializer,
                             PasswordChangeSerializer)
from rest_framework.viewsets import ModelViewSet

from .models import User, Subscribe


class CustomUserViewSet(ModelViewSet):
    """Вьюсет Users для создания и просмотра подписок."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    search_fields = ('username', 'email')
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    @action(detail=True,
            url_path='me',
            methods=('GET', 'PATCH'),
            permission_classes=(IsAuthenticated,))
    def get_or_patch_self_profile(self, request):
        """Пользователь может изменить и получить данные о себе."""
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status=HTTPStatus.OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(detail=True,
            url_path='subscribe',
            methods=('POST', 'DELETE', ),
            permission_classes=(IsAuthenticated,))
    def subscribe_and_unsubscribe(self, request, pk):
        """Создание подписки и отписки."""
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = SubscribeSerializer(author, data=request.data)
            serializer.is_valid(raise_exception=True)
            subscribe = Subscribe.objects.create(user=request.user, author=author)
            subscribe.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=request.user,
                                             author=author)
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        methods=('GET', ),)
    def all_user_subscriptions(self, request):
         return Subscribe.objects.filter(user=request.user).all()

    @action(detail=False,
            url_path='set_password',
            methods=('POST', ),
            permission_classes=(IsAuthenticated,))
    def change_password(self, request):
        serializer = PasswordChangeSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
              'Пароль успешно изменен!', status=HTTPStatus.NO_CONTENT
            )
