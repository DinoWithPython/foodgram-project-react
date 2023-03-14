from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit_of_measurement')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
