from http import HTTPStatus

from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from api.serializers import (SubscribeSerializer, UserCreateSerializer,
                             UserCreationSerializer)

from .models import Subscribe, User
from .permissions import IsAdminAuthorOrReadOnly
from .pagination import PageLimitPagination

class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User и Subscribe."""
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny, )

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = request.user
        queryset = user.subscriber.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
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
                return Response(
                    f'На себя подписаться нельзя',
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
