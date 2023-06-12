from http import HTTPStatus

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from api.pagination import LimitPageNumberPagination
from api.serializers import FollowSerializer
from .models import CustomUser, Subscribe


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет User."""
    queryset = CustomUser.objects.all()
    http_method_names = ('post', 'get', 'delete')
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitOffsetPagination

    @action(detail=True, url_path='subscribe',
            methods=['POST', 'DELETE'],)
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
            permission_classes=(IsAuthenticated, )
        )
        def subscriptions(self, request):
            user = request.user
            return User.objects.filter(subscribing__user=user).all()
