from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class CustomUser(AbstractUser):
    """Модель пользователя."""
    first_name = models.CharField(
        max_length=settings.FIRST_USERNAME_MAX_LENGHT,
        blank=True,
    )
    last_name = models.CharField(
        max_length=settings.LAST_USERNAME_MAX_LENGHT,
        blank=True,
    )
    username = models.CharField(
        'Никнейм',
        max_length=settings.USERNAME_MAX_LENGHT,
        null=False,
        blank=False,
        unique=True,
        validators=(validate_regex_username,
                    validate_username),
    )
    email = models.EmailField(
        'Email',
        max_length=settings.EMAIL_MAX_LENGHT,
        null=False,
        unique=True,
        blank=False,
    )

    class Meta:
        """Мета класс User."""
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """ Subscribe модель """
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        on_delete=models.CASCADE,
        null=True,
        help_text='Подписчик автора'
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        on_delete=models.CASCADE,
        null=True,
        help_text='Автор'
    )

    class Meta:
        """ Metaclass Subscribe."""
        verbose_name = 'Подписки'
        UniqueConstraint(fields=['author', 'user'],
                         name='re-subscription')
        CheckConstraint(
            name='prevent_self_subscription',
            check=~models.Q(user=models.F('author')), )

    def __str__(self):
        return '{} подписан на {}'.format(self.user, self.author)