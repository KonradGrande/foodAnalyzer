from .ranker import Ranker
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Meal,
    Reaction,
)
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
        ingredients = recipe.recipeingredient_set.all()
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
        ingredients = recipe.recipeingredient_set.all()
        context["recipe"] = recipe
        context["ingredients"] = ingredients
        return context


class RecipeIngredientCreateView(LoginRequiredMixin, CreateView):
    template_name = "ingredient_recipe/create.html"
    model = RecipeIngredient
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


class RecipeIngredientUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "ingredient_recipe/update.html"
    model = RecipeIngredient
    fields = ["ingredient", "amount"]

    def form_valid(self, form):
        recipe = Recipe.objects.get(id=self.kwargs["recipe_pk"])
        ingredient = RecipeIngredient.objects.get(id=self.kwargs["pk"])
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


class RecipeIngredientDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "ingredient_recipe/delete.html"
    model = RecipeIngredient

    def get_success_url(self):
        return reverse(
            "recipe:update", kwargs={"pk": self.kwargs["recipe_pk"]}
        )


class RankingView(LoginRequiredMixin, TemplateView):
    template_name = "ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["ranking"] = Ranker(user).get_ranking()
        return context


SUCCESS = "success"
WARNING = "warning"
INFO = "info"
DANGER = "danger"


def panel(type, title, body=None, footer=None):
    p = f"""<div class="panel panel-{type}">
    <div class="panel-heading">{title}</div>"""
    if body:
        p += f"""<div class="panel-body">{body}</div>"""
    if footer:
        p += f"""<div class="panel-footer">{footer}</div>"""
    p += "</div>"
    return p


def list(items):
    l = "<ul>"
    for item in items:
        l += f"<li>{item}</li>"
    l += "</ul>"
    return l


def rows(items):
    r = ""
    for item in items:
        r += f"""
        <div class="row">
            <div class="col-sm-1"></div>
            <div class="col-sm-10">
                {item}
            </div>
            <div class="col-xs-1"></div>
        </div>"""
    return r


class FoodHistoryView(LoginRequiredMixin, TemplateView):
    template_name = "food/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ranker = Ranker(self.request.user)

        suspect = None
        for key, sus in ranker.suspects.items():
            if sus.name == self.kwargs["suspect"]:
                suspect = sus

        panels = []
        amount_in_reactions = ranker.suspect_amount_per_reaction(suspect.name)
        for reaction in ranker.reactions:
            type = DANGER if reaction.reaction else SUCCESS
            panels.append(
                panel(
                    type,
                    f"{reaction.date}",
                    body=f"{reaction.diary}",
                    footer=f"Amount of {suspect.name} consumed: {amount_in_reactions[reaction]}",
                )
            )

        context["title"] = f"<h1>{suspect.name}</h1>"
        context["panels"] = panels
        return context
