from http import HTTPStatus

from users.models import Subscribe


def validate(self, value):
    author = self.instance
    user = self.context.get('request').user
    if Subscribe.objects.filter(author=author, user=user).exists():
        raise ValidationError(
            detail='Вы уже подписаны на этого автора',
            code=HTTPStatus.BAD_REQUEST
        )
    if user == author:
        raise ValidationError(
            detail='Подписаться на самого себя невозможно ',
            code=HTTPStatus.BAD_REQUEST
        )
    return value
