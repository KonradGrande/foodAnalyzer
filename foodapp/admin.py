from django.contrib import admin
from .models import Ingredient, Meal, Reaction

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Meal)
admin.site.register(Reaction)
