from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from tags.models import Tag
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
)
from users.models import Subscription, User
from api.serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from api.filters import RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=("get",),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = user.follower.all()
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        serializer_class=SubscriptionSerializer,
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == "POST":
            if user == author:
                raise exceptions.ValidationError(
                    "Невозможно подписаться на себя же."
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError("Подписка уже оформлена.")

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Subscription.objects.filter(
                user=user, author=author
            ).exists():
                raise exceptions.ValidationError(
                    "Подписка не была оформлена, либо уже отменена."
                )

            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    def actions(self, request, model, text_in_exception, pk=None):
        user = self.request.user
        recipe = get_object_or_404(model, pk=pk)

        if self.request.method == "POST":
            if model.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    f"Рецепт уже {text_in_exception}."
                )

            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={"request": request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not model.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    f"Рецепта нет {text_in_exception}, либо он удален."
                )

            obj = get_object_or_404(model, user=user, recipe=recipe)
            obj.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        self.actions(request, Favorite, "в избранном", pk=None)

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        self.actions(request, ShoppingCart, "в списке покупок", pk=None)

    @action(
        detail=False, methods=("get",), permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy = (
            RecipeIngredients.objects.filter(recipe__in=recipes)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )

        purchased = [
            "Список покупок:",
        ]
        for item in buy:
            ingredient = Ingredient.objects.get(pk=item["ingredient"])
            amount = item["amount"]
            purchased.append(
                f"{ingredient.name}: {amount}, "
                f"{ingredient.unit_of_measurement}"
            )
        purchased_in_file = "\n".join(purchased)

        response = HttpResponse(purchased_in_file, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping-list.txt"

        return response
