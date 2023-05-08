#!/usr/bin/env python3

from dataclasses import dataclass
from .models import Meal, Reaction
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

    def suspects_in_reaction_window(self, reaction_date):
        """How much of each suspect the user ate before the reaction."""
        day_before = reaction_date - timedelta(days=1)
        relevant_meals = self.meals.filter(
            date__range=[day_before, reaction_date]
        )

        suspects_in_window = {}

        def log_suspect(suspect_key, amount):
            if suspect_key in suspects_in_window.keys():
                suspects_in_window[suspect_key] += amount
            else:
                suspects_in_window[suspect_key] = amount

        for meal in relevant_meals:
            for ingredient in meal.food.recipeingredient_set.all():
                allergens = ingredient.ingredient.ingredientallergen_set.all()
                if allergens:
                    for allergen in allergens:
                        log_suspect(
                            allergen.allergen.name,
                            amount_allergen(
                                meal.amount,
                                ingredient.percent,
                                allergen.percent,
                            ),
                        )
                else:
                    log_suspect(
                        ingredient.ingredient.name,
                        amount_ingredient(meal.amount, ingredient.percent),
                    )
        return suspects_in_window

    def analyse_reactions(self):
        for reaction in self.reactions:
            suspects_in_window = self.suspects_in_reaction_window(
                reaction.date
            )
            for suspect_name, amount in suspects_in_window.items():
                if suspect_name in self.suspects.keys():
                    if self.suspects[suspect_name].threshold <= amount:
                        if reaction.reaction:
                            self.suspects[suspect_name].reactivity += 1
                        else:
                            self.suspects[suspect_name].reactivity = 0
                    else:
                        if reaction.reaction:
                            self.suspects[suspect_name].reactivity += 1
                            self.suspects[suspect_name].threshold = amount
                else:
                    self.suspects[suspect_name] = Suspect(
                        suspect_name,
                        amount,
                    )

    def get_ranking(self):
        ranking = []

        for food, suspect in self.suspects.items():
            if suspect.reactivity != 0:
                ranking.append(suspect)

        ranking.sort(key=lambda x: x.reactivity, reverse=True)

        return ranking

    def suspect_amount_per_reaction(self, suspect_name):
        amount_per_reaction = {}
        for reaction in self.reactions:
            suspects_in_window = self.suspects_in_reaction_window(
                reaction.date
            )

            if suspect_name in suspects_in_window.keys():
                amount_per_reaction[reaction] = suspects_in_window[
                    suspect_name
                ]
            else:
                amount_per_reaction[reaction] = 0
        return amount_per_reaction


def amount_ingredient(meal_amount, ingredient_percent):
    """Amount of ingredient in meal."""
    return meal_amount * ingredient_percent / 100


def amount_allergen(meal_amount, ingredient_percent, allergen_percent):
    """Amount of allergen in ingredient in meal."""
    return (
        amount_ingredient(meal_amount, ingredient_percent)
        * allergen_percent
        / 100
    )
