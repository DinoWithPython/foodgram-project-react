import string

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Модель пользователей."""
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username

    def clean(self):
        forbidden_characters= []
        for symbol in self.username:
            if (symbol in string.punctuation 
                and symbol not in '.@+-_'):
                forbidden_characters.append(symbol)
            if symbol in string.whitespace:
                forbidden_characters.append(symbol)
        if len(forbidden_characters) != 0:
            raise ValidationError(
                f'Введены не допустимые символы: {"".join(forbidden_characters)}'
                f'Не допускаются: пробел(перенос строки и т.п.) и символы, кроме . @ + - _')


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_cannot_follow_himself'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
