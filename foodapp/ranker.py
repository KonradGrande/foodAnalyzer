#!/usr/bin/env python3

from dataclasses import dataclass
from .models import Ingredient, RecipeIngredient, Meal, Reaction
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
            irs = RecipeIngredient.objects.filter(recipe=meal.food)
            for ingredient in irs:
                gluten = ingredient.ingredient.gluten
                lactose = ingredient.ingredient.lactose
                if gluten == 0 and lactose == 0:
                    log_suspect(
                        ingredient.ingredient.id,
                        ingredient.amount * meal.amount / 100,
                    )
                else:
                    log_suspect("lactose", lactose * meal.amount / 100)
                    log_suspect("gluten", gluten * meal.amount / 100)
        return suspects_in_window

    def suspect_key_to_suspect_name(self, key):
        if key == "lactose" or key == "gluten":
            return key
        return Ingredient.objects.get(id=key).name

    def suspect_name_to_suspect_key(self, name):
        if name == "lactose" or name == "gluten":
            return name
        return Ingredient.objects.get(name=name).id

    def analyse_reactions(self):
        for reaction in self.reactions:
            suspects_in_window = self.suspects_in_reaction_window(
                reaction.date
            )
            for suspect_key, amount in suspects_in_window.items():
                if suspect_key in self.suspects.keys():
                    if self.suspects[suspect_key].threshold <= amount:
                        if reaction.reaction:
                            self.suspects[suspect_key].reactivity += 1
                        else:
                            self.suspects[suspect_key].reactivity = 0
                    else:
                        if reaction.reaction:
                            self.suspects[suspect_key].reactivity += 1
                            self.suspects[suspect_key].threshold = amount
                else:
                    name = self.suspect_key_to_suspect_name(suspect_key)

                    self.suspects[suspect_key] = Suspect(
                        name,
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

            key = self.suspect_name_to_suspect_key(suspect_name)

            if key in suspects_in_window.keys():
                amount_per_reaction[reaction] = suspects_in_window[key]
            else:
                amount_per_reaction[reaction] = 0
        return amount_per_reaction
