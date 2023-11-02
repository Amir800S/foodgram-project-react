from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint

from .validators import validate_regex_username, validate_username


class User(AbstractUser):
    """Модель пользователя."""

    first_name = models.CharField(
        max_length=settings.FIRST_USERNAME_MAX_LENGHT,
        blank=True,
        null=False,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=settings.LAST_USERNAME_MAX_LENGHT,
        blank=True,
        null=False,
        verbose_name="Фамилия",
    )
    username = models.CharField(
        "Никнейм",
        max_length=settings.USERNAME_MAX_LENGHT,
        null=False,
        blank=True,
        unique=True,
        validators=(validate_regex_username, validate_username),
    )
    email = models.EmailField(
        "Email",
        max_length=settings.EMAIL_MAX_LENGHT,
        null=False,
        unique=True,
        blank=False,
    )
    password = models.CharField(
        "Пароль",
        max_length=settings.PASSWORD_MAX_LENGHT,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        related_name="subscriber",
        on_delete=models.CASCADE,
        null=True,
        help_text="Подписчик автора",
    )
    author = models.ForeignKey(
        User,
        related_name="subscribing",
        on_delete=models.CASCADE,
        null=True,
        help_text="Автор",
    )

    class Meta:
        verbose_name = "Подписки"
        UniqueConstraint(fields=["author", "user"], name="re-subscription")
        CheckConstraint(
            name="prevent_self_subscription",
            check=~models.Q(user=models.F("author")),
        )

    def __str__(self):
        return "{} подписан на {}".format(self.user, self.author)
