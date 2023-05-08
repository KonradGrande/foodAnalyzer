#!/usr/bin/env sh

python manage.py graph_models -a -I Allergen,IngredientAllergen,Ingredient,RecipeIngredient,Recipe,Meal,User,Reaction -o models.png
