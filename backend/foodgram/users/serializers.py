from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription
from recipes.models import Recipe
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Проверка подписки."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')


    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()




class CustomUserCreateSerializer(UserCreateSerializer):
    """При создании пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password')


class SubscriptionSerializer(CustomUserSerializer):
    """Подписка на рецепты."""
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')


    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        from recipes.serializers import ShortRecipeSerializer
        author_recipes = Recipe.objects.filter(author=obj)

        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author_recipes = author_recipes[:int(recipes_limit)]

        if author_recipes:
            serializer = ShortRecipeSerializer(
                author_recipes,
                context={'request': self.context.get('request')},
                many=True
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

