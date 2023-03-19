from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers

from recipes.models import Recipe
from tags.models import Tag
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
)
from tags.models import Tag
from users.models import Subscription, User
from api.pagination import PageNumberPagination


class CustomUserSerializer(UserSerializer):
    """Проверка подписки."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """При создании пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )


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
        from api.serializers import ShortRecipeSerializer

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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    unit_of_measurement = serializers.ReadOnlyField(
        source="ingredient.unit_of_measurement"
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "unit_of_measurement", "amount")


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Количество ингредиентов не может быть меньше 1."
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)

        return serializer.data

    def get_queryset(self, model):
        user = self.context["request"].user
        return model.objects.filter(user=user, recipe=model).exists()

    def get_is_favorited(self, obj):
        return self.get_queryset(model=Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_queryset(obmodelj=ShoppingCart)

    class Meta:
        model = Recipe
        exclude = ("-pub_date",)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Время приготовления не может быть меньше 1!"
            ),
        )
    )

    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError("Добавьте хотя бы один тег!")

        return value

    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                "Добавьте хотя бы один ингредиент!"
            )

        ingredients = [item["id"] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    "Рецепт не может включать два одинаковых ингредиента!"
                )

        return value

    def create(self, validated_data):
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient["amount"]
                ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={"amount": amount},
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )

        return serializer.data

    class Meta:
        model = Recipe
        exclude = ("-pub_date",)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
