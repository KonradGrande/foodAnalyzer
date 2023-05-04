"""food URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from foodapp import views

account_urls = (
    [
        path("", include("django.contrib.auth.urls")),
        path("signup/", views.SignupView.as_view(), name="signup"),
    ],
    "account",
)

meal_urls = (
    [
        path(
            "create/",
            views.MealCreateView.as_view(),
            name="create",
        ),
        path(
            "all/",
            views.MealAllView.as_view(),
            name="all",
        ),
        path(
            "delete/<int:pk>",
            views.MealDeleteView.as_view(),
            name="delete",
        ),
    ],
    "meal",
)

reaction_urls = (
    [
        path(
            "create/",
            views.ReactionCreateView.as_view(),
            name="create",
        ),
        path(
            "update/<int:pk>",
            views.ReactionUpdateView.as_view(),
            name="update",
        ),
        path(
            "all/",
            views.ReactionAllView.as_view(),
            name="all",
        ),
        path(
            "delete/<int:pk>",
            views.ReactionDeleteView.as_view(),
            name="delete",
        ),
    ],
    "reaction",
)

ingredient_urls = (
    [
        path("create/", views.IngredientCreateView.as_view(), name="create"),
        path(
            "update/<int:pk>",
            views.IngredientUpdateView.as_view(),
            name="update",
        ),
        path(
            "delete/<int:pk>",
            views.IngredientDeleteView.as_view(),
            name="delete",
        ),
        path(
            "detail/<int:pk>",
            views.IngredientDetailView.as_view(),
            name="detail",
        ),
        path("list/", views.IngredientListView.as_view(), name="list"),
    ],
    "ingredient",
)

recipe_ingredient_urls = (
    [
        path(
            "create/",
            views.RecipeIngredientCreateView.as_view(),
            name="create",
        ),
        path(
            "delete/<int:pk>",
            views.RecipeIngredientDeleteView.as_view(),
            name="delete",
        ),
        path(
            "update/<int:pk>",
            views.RecipeIngredientUpdateView.as_view(),
            name="update",
        ),
    ],
    "ingredients",
)

recipe_urls = (
    [
        path("create/", views.RecipeCreateView.as_view(), name="create"),
        path(
            "update/<int:pk>", views.RecipeUpdateView.as_view(), name="update"
        ),
        path(
            "delete/<int:pk>",
            views.RecipeDeleteView.as_view(),
            name="delete",
        ),
        path(
            "detail/<int:pk>",
            views.RecipeDetailView.as_view(),
            name="detail",
        ),
        path("list/", views.RecipeListView.as_view(), name="list"),
        path("<int:recipe_pk>/ingredients/", include(recipe_ingredient_urls)),
    ],
    "recipe",
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include(account_urls)),
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("meal/", include(meal_urls)),
    path("reaction/", include(reaction_urls)),
    path("ingredient/", include(ingredient_urls)),
    path("recipe/", include(recipe_urls)),
    path("ranking/", views.RankingView.as_view(), name="ranking"),
    path(
        "food/history/<str:suspect>",
        views.FoodHistoryView.as_view(),
        name="history",
    ),
]
