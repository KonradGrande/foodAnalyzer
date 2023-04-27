from django.db.models import Q
from dataclasses import dataclass
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import Ingredient, Recipe, IngredientRecipe, Meal, Reaction
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from datetime import timedelta


class SignupView(FormView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = "/accounts/login/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        meals = Meal.objects.filter(user=self.request.user, date=today)

        try:
            reaction = Reaction.objects.get(
                user=self.request.user, date=today
            )
        except Reaction.DoesNotExist:
            reaction = None

        context["meals"] = meals
        context["reaction"] = reaction
        return context


class MealCreateView(LoginRequiredMixin, CreateView):
    template_name = "meal/create.html"
    model = Meal
    fields = [
        "date",
        "food",
        "amount",
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MealDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "meal/delete.html"
    model = Meal

    def get_queryset(self):
        return Meal.objects.filter(
            user=self.request.user, id=self.kwargs["pk"]
        )

    def get_success_url(self):
        return reverse("dashboard")


class MealAllView(LoginRequiredMixin, TemplateView):
    template_name = "meal/all.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meals = Meal.objects.filter(user=self.request.user).order_by("-date")

        days = {}
        for meal in meals:
            key = meal.date
            if key not in days.keys():
                days[key] = [meal]
            else:
                days[key].append(meal)

        daylist = []
        for key in days.keys():
            daylist.append([key, days[key]])

        context["daylist"] = daylist
        return context


class ReactionAllView(LoginRequiredMixin, ListView):
    template_name = "reaction/all.html"
    model = Reaction
    context_object_name = "reactions"

    def get_queryset(self):
        return Reaction.objects.filter(user=self.request.user).order_by(
            "-date"
        )


class ReactionCreateView(LoginRequiredMixin, CreateView):
    template_name = "reaction/create.html"
    model = Reaction
    fields = ["date", "reaction", "diary"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            form.add_error("date", e)
            return self.form_invalid(form)


class ReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "reaction/update.html"
    model = Reaction
    fields = ["date", "reaction", "diary"]

    def get_queryset(self):
        return Reaction.objects.filter(
            user=self.request.user, id=self.kwargs["pk"]
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            form.add_error("date", e)
            return self.form_invalid(form)


class ReactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "reaction/delete.html"
    model = Reaction

    def get_queryset(self):
        return Reaction.objects.filter(
            user=self.request.user, id=self.kwargs["pk"]
        )

    def get_success_url(self):
        return reverse("dashboard")


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


class RankingView(LoginRequiredMixin, TemplateView):
    template_name = "ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["ranking"] = Ranker(user).get_ranking()
        return context


class FoodHistoryView(LoginRequiredMixin, DetailView):
    template_name = "food/history.html"

    def get_queryset(self):
        return Ingredient.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        recipe = self.kwargs["pk"]
        meals = Meal.objects.filter(user=user, food=recipe).order_by("-date")
        reactions = Reaction.objects.filter(user=user).order_by("-date")

        days = {}
        for meal in meals:
            if meal.date in days.keys():
                days[meal.date]["meals"].append(meal)
            else:
                days[meal.date] = {"meals": [meal]}

        for reaction in reactions:
            if reaction.date in days.keys():
                days[reaction.date]["reaction"] = reaction
            else:
                days[reaction.date] = {"reaction": reaction}

        print(days)

        daylist = []
        for date, mr in days.items():
            if "meals" in mr.keys():
                meals = mr["meals"]
            else:
                meals = []
            if "reaction" in mr.keys():
                reaction = mr["reaction"]
            else:
                reaction = None
            daylist.append((date, meals, reaction))

        context["daylist"] = daylist
        return context


class IngredientCreateView(LoginRequiredMixin, CreateView):
    template_name = "ingredient/create.html"
    model = Ingredient
    fields = [
        "name",
        "lactose",
        "gluten",
    ]


class IngredientUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "ingredient/update.html"
    model = Ingredient
    fields = [
        "name",
        "lactose",
        "gluten",
    ]


class IngredientDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "ingredient/delete.html"
    model = Ingredient

    def get_success_url(self):
        return reverse("ingredient:list")


class IngredientListView(LoginRequiredMixin, ListView):
    template_name = "ingredient/list.html"
    model = Ingredient

    def get_queryset(self):
        query = self.request.GET.get("ingredient")

        if query:
            return Ingredient.objects.filter(Q(name__icontains=query))
        else:
            return Ingredient.objects.all()


class IngredientDetailView(LoginRequiredMixin, DetailView):
    template_name = "ingredient/detail.html"
    model = Ingredient


class RecipeCreateView(LoginRequiredMixin, CreateView):
    template_name = "recipe/create.html"
    model = Recipe
    fields = ["name"]


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "recipe/update.html"
    model = Recipe
    fields = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipe = Recipe.objects.get(id=self.kwargs["pk"])
        ingredients = recipe.ingredientrecipe_set.all()
        context["recipe"] = recipe
        context["ingredients"] = ingredients
        return context


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "recipe/delete.html"
    model = Recipe

    def get_success_url(self):
        return reverse("recipe:list")


class RecipeListView(LoginRequiredMixin, ListView):
    template_name = "recipe/list.html"
    model = Recipe

    def get_queryset(self):
        query = self.request.GET.get("recipe")

        if query:
            return Recipe.objects.filter(Q(name__icontains=query))
        else:
            return Recipe.objects.all()


class RecipeDetailView(LoginRequiredMixin, DetailView):
    template_name = "recipe/detail.html"
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipe = Recipe.objects.get(id=self.kwargs["pk"])
        ingredients = recipe.ingredientrecipe_set.all()
        context["recipe"] = recipe
        context["ingredients"] = ingredients
        return context


class IngredientRecipeCreateView(LoginRequiredMixin, CreateView):
    template_name = "ingredient_recipe/create.html"
    model = IngredientRecipe
    fields = ["ingredient", "amount"]

    def form_valid(self, form):
        recipe = Recipe.objects.get(id=self.kwargs["recipe_pk"])
        form.instance.recipe = recipe
        amount = form.instance.amount

        if recipe.is_amount_possible(amount):
            return super().form_valid(form)
        else:
            total = recipe.get_sum_ingredients() + amount
            form.add_error(
                "amount",
                f"The ingredients in the recipe would add up to {total}%",
            )
            return self.form_invalid(form)


class IngredientRecipeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "ingredient_recipe/update.html"
    model = IngredientRecipe
    fields = ["ingredient", "amount"]

    def form_valid(self, form):
        recipe = Recipe.objects.get(id=self.kwargs["recipe_pk"])
        ingredient = IngredientRecipe.objects.get(id=self.kwargs["pk"])
        amount = form.instance.amount

        diff = amount - ingredient.amount

        if recipe.is_amount_possible(diff):
            return super().form_valid(form)
        else:
            total = recipe.get_sum_ingredients() + diff
            form.add_error(
                "amount",
                f"The ingredients in the recipe would add up to {total}%",
            )
            return self.form_invalid(form)


class IngredientRecipeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "ingredient_recipe/delete.html"
    model = IngredientRecipe

    def get_success_url(self):
        return reverse(
            "recipe:update", kwargs={"pk": self.kwargs["recipe_pk"]}
        )
