from django_filters import ModelMultipleChoiceFilter

from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe
from tags.models import Tag
from users.models import User


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    def get_queryset(self, field, value):
        field = self.request.query_params.get(field)
        if value:
            return self.get_queryset().filter(field__user=self.request.user)
        return self.get_queryset()

    def is_favorited_method(self, queryset, name, value):
        self.get_queryset(field="favorite", value=value)

    def is_in_shopping_cart_method(self, queryset, name, value):
        self.get_queryset(field="shopping_list", value=value)

    class Meta:
        model = Recipe
        fields = ("author", "tags")
