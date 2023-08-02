from http import HTTPStatus

from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from api.serializers import (SubscribeSerializer,
                             UserSerializer,
                             PasswordChangeSerializer,
                             UserCreationSerializer)
from rest_framework.viewsets import ModelViewSet

from .models import User, Subscribe


class CustomUserViewSet(ModelViewSet):
    """Вьюсет Users для создания и просмотра подписок."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ('patch', 'post', 'get', 'delete',)
    pagination_class = LimitOffsetPagination
    serializer_class = UserCreationSerializer

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
            methods=('POST', 'DELETE', ),)
    def subscribe_and_unsubscribe(self, request):
        """Создание подписки и отписки."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(author, data=request.data)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=HTTPStatus.OK)

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