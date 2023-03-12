from rest_framework import serializers

from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
