from django.utils import timezone
from django.shortcuts import render
from .models import Food, Meal, Reaction
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

        reactions = Reaction.objects.filter(
            user=self.request.user, date=today
        )

        context["meals"] = meals
        context["reactions"] = reactions
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
        return super().form_valid(form)


class ReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "reaction/update.html"
    model = Reaction
    fields = ["date", "reaction", "diary"]

    def get_queryset(self):
        return Reaction.objects.filter(
            user=self.request.user, id=self.kwargs["pk"]
        )


class ReactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "reaction/delete.html"
    model = Reaction

    def get_queryset(self):
        return Reaction.objects.filter(
            user=self.request.user, id=self.kwargs["pk"]
        )

    def get_success_url(self):
        return reverse("dashboard")


class RankingView(LoginRequiredMixin, TemplateView):
    template_name = "ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        meals = Meal.objects.filter(user=user).order_by("-date")
        reactions = Reaction.objects.filter(user=user).order_by("-date")

        # id of the food
        food_eaten = meals.values_list("food", flat=True).distinct()
        food_eaten = [Food.objects.get(id=id) for id in food_eaten]

        foods = dict([(food, 0) for food in food_eaten])

        for reaction in reactions:
            day_before = reaction.date - timedelta(days=1)
            relevant_meals = meals.filter(
                date__range=[day_before, reaction.date]
            )  # should be extended to include day before
            if reaction.reaction:
                for meal in relevant_meals:
                    foods[meal.food] += 1
            else:
                for meal in relevant_meals:
                    foods[meal.food] = 0
        ranking = []
        for food, rank in foods.items():
            if rank != 0:
                ranking.append((food, rank))

        ranking.sort(key=lambda x: x[1], reverse=True)
        context["ranking"] = ranking
        return context


class FoodHistoryView(LoginRequiredMixin, DetailView):
    template_name = "food/history.html"

    def get_queryset(self):
        return Food.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        food = self.kwargs["pk"]
        meals = Meal.objects.filter(user=user, food=food).order_by("-date")
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
