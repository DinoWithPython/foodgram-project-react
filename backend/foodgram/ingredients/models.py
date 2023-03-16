from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=80,
        verbose_name="Название ингредиента",
        help_text="Название ингредиента",
    )
    unit_of_measurement = models.CharField(
        max_length=15,
        verbose_name="Единица измерения ингредиента",
        help_text="Единица измерения ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

        constraints = (
            models.UniqueConstraint(
                fields=("name", "unit_of_measurement"), name="unique_ingredient"
            ),
        )

    def __str__(self):
        return self.name
