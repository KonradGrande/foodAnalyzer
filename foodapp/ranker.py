#!/usr/bin/env python3

from dataclasses import dataclass
from .models import Ingredient, IngredientRecipe, Meal, Reaction
from datetime import timedelta


@dataclass
class Suspect:
    name: str
    threshold: int = 0
    reactivity: int = 0


class Ranker:
    def __init__(self, user):
        self.user = user
        self.meals = Meal.objects.filter(user=user).order_by("-date")
        self.reactions = Reaction.objects.filter(user=user).order_by("-date")
        self.suspects = {}
        self.analyse_reactions()

    def ingredients_in_reaction_window(self, reaction_date):
        """How much of each ingredient the user ate before the reaction."""
        day_before = reaction_date - timedelta(days=1)
        relevant_meals = self.meals.filter(
            date__range=[day_before, reaction_date]
        )

        ingredients = {}

        def log_ingredient(ingredient, amount):
            if ingredient in ingredients.keys():
                ingredients[ingredient] += amount
            else:
                ingredients[ingredient] = amount

        for meal in relevant_meals:
            irs = IngredientRecipe.objects.filter(recipe=meal.food)
            for ingredient in irs:
                gluten = ingredient.ingredient.gluten
                lactose = ingredient.ingredient.lactose
                if gluten == 0 and lactose == 0:
                    log_ingredient(
                        ingredient.ingredient.id,
                        ingredient.amount * meal.amount,
                    )
                else:
                    log_ingredient("lactose", lactose * meal.amount)
                    log_ingredient("gluten", gluten * meal.amount)
        return ingredients

    def analyse_reactions(self):
        def analyse_reaction(reaction):
            ingredients = self.ingredients_in_reaction_window(reaction.date)
            for ingredient_key, amount in ingredients.items():
                if ingredient_key in self.suspects.keys():
                    if self.suspects[ingredient_key].threshold < amount:
                        if reaction.reaction:
                            self.suspects[ingredient_key].reactivity += 1
                        else:
                            self.suspects[ingredient_key].reactivity = 0
                    else:
                        if reaction.reaction:
                            self.suspects[ingredient_key].reactivity += 1
                            self.suspects[ingredient_key].threshold = amount
                else:
                    if (
                        ingredient_key == "lactose"
                        or ingredient_key == "gluten"
                    ):
                        name = ingredient_key
                    else:
                        name = Ingredient.objects.get(id=ingredient_key).name
                    self.suspects[ingredient_key] = Suspect(
                        name,
                        amount,
                    )

        for reaction in self.reactions:
            analyse_reaction(reaction)

    def get_ranking(self):
        ranking = []

        for food, suspect in self.suspects.items():
            if suspect.reactivity != 0:
                ranking.append(suspect)

        ranking.sort(key=lambda x: x.reactivity, reverse=True)

        return ranking

    def ingredient_amount_per_reaction(self, ingredient):
        ingredient_per_reaction = {}
        for reaction in self.reactions:
            ingredients = self.ingredients_in_reaction_window(reaction.date)
            if ingredient in ingredients.keys():
                ingredient_per_reaction[reaction] = ingredients[ingredient]
            else:
                ingredient_per_reaction[reaction] = 0
        return ingredient_per_reaction
