from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription
from recipes.models import Recipe
from users.models import User
from api.pagination import PageNumberPagination


class CustomUserSerializer(UserSerializer):
    """Проверка подписки."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "is_subscribed")

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """При создании пользователя."""

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "password")


class SubscriptionSerializer(CustomUserSerializer, PageNumberPagination):
    """Подписка на рецепты."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        from recipes.serializers import ShortRecipeSerializer

        author_recipes = Recipe.objects.filter(author=obj)

        if author_recipes:
            serializer = ShortRecipeSerializer(
                author_recipes,
                context={"request": self.context.get("request")},
                many=True,
            )
            return self.get_paginated_response(serializer.data)

        return []

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return Recipe.objects.filter(author=obj).count()
