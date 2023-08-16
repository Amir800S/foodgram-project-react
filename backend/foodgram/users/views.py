from http import HTTPStatus

from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from api.serializers import (SubscribeSerializer,
                             UserCreateSerializer,
                             PasswordChangeSerializer)
from .permissions import IsAdminAuthorOrReadOnly

from .models import User, Subscribe


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminAuthorOrReadOnly, )

    @action(
        methods=('get', ),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Получить подписки пользователя."""
        serializer = SubscribeSerializer(
            self.paginate_queryset(
                Subscribe.objects.filter(user=request.user)
            ), many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete', ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Функция подписки и отписки."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        obj = Subscribe.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if user == author:
                return Response(f'На себя подписаться нельзя',
                                status=HTTPStatus.BAD_REQUEST
                                )
            if obj.exists():
                return Response(
                    f'Вы уже подписаны на {author.username}',
                    status=HTTPStatus.BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=user, author=author),
                context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if user == author:
            return Response(
                f'Вы не можете отписаться от самого себя',
                status=HTTPStatus.BAD_REQUEST
            )
        if obj.exists():
            obj.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            f'Вы уже отписались от {author.username}',
            status=HTTPStatus.BAD_REQUEST
        )
