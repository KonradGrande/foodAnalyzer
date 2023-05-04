from django.contrib import admin
from .models import (
    Ingredient,
    Meal,
    Reaction,
    RecipeIngredient,
    Allergen,
    IngredientAllergen,
    Recipe,
)

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Meal)
admin.site.register(Reaction)
admin.site.register(RecipeIngredient)
admin.site.register(Allergen)
admin.site.register(IngredientAllergen)
admin.site.register(Recipe)
