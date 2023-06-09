from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    allergens = models.ManyToManyField(Allergen, through="IngredientAllergen")

    def get_sum_allergens(self):
        allergens = self.ingredientallergen_set.all()
        total = 0
        for allergen in allergens:
            total += allergen.percent
        return total

    def is_percent_possible(self, percent):
        if self.get_sum_allergens() + percent <= 100:
            return True
        return False

    def get_absolute_url(self):
        return reverse("ingredient:list")

    def __str__(self):
        return self.name


class IngredientAllergen(models.Model):
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    def get_absolute_url(self):
        return reverse("ingredient:update", kwargs={"pk": self.ingredient.id})


class Recipe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient"
    )

    def get_sum_ingredients(self):
        ingredients = self.ingredientrecipe_set.all()
        total = 0
        for ingredient in ingredients:
            total += ingredient.percent
        return total

    def is_percent_possible(self, percent):
        if self.get_sum_ingredients() + percent <= 100:
            return True
        return False

    def get_absolute_url(self):
        return reverse("recipe:list")

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    def get_absolute_url(self):
        return reverse("recipe:update", kwargs={"pk": self.recipe.id})


class Meal(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="user"
    )
    food = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def get_absolute_url(self):
        return reverse("meal:all")

    def __str__(self):
        return (
            f"{self.user} ate {self.amount}g of {self.food.name} {self.date}"
        )


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    NO = 0
    YES = 1
    reaction = models.IntegerField(
        choices=[(NO, "No"), (YES, "Yes")], default=NO
    )
    diary = models.TextField()

    def get_absolute_url(self):
        return reverse("reaction:all")

    def __str__(self):
        if self.reaction:
            return f"{self.user} had a reaction {self.date}"
        else:
            return f"{self.user} did not have a reaction {self.date}"

    class Meta:
        unique_together = ("user", "date")
