from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from api.serializers import SubscribeSerializer, UserSerializer
from .models import User, Subscribe


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет Users для создания и просмотра подписок."""
    queryset = User.objects.all()
    http_method_names = ('post', 'get', 'delete')
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    @action(detail=False,
            url_path='me',
            methods=('GET',),
            permission_classes=(IsAuthenticated,))
    def get_or_patch_self_profile(self, request):
        """Пользователь может изменить и получить данные о себе."""
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(detail=True,
            url_path='subscribe',
            methods=('POST', 'DELETE'),)
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
        methods=('POST', 'DELETE'),)
    def all_user_subscriptions(self, request):
        return User.objects.filter(
            subscribing__user=request.user).all()
    @action(detail=False,
            methods=('post', ),
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            'Пароль успешно изменен!', status=HTTPStatus.NO_CONTENT
        )