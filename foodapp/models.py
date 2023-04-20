from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lactose = models.PositiveIntegerField()
    gluten = models.PositiveIntegerField()

    def get_absolute_url(self):
        return reverse("ingredient:list")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe"
    )

    def get_absolute_url(self):
        return reverse("recipe:list")


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def get_absolute_url(self):
        return reverse("recipe:update", kwargs={"pk": self.recipe.id})


class Meal(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="user"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def get_absolute_url(self):
        return reverse("meal:all")

    def __str__(self):
        return (
            f"{self.user} ate {self.amount}g of {self.ingredient} {self.date}"
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
        return reverse("rection:all")

    def __str__(self):
        if self.reaction:
            return f"{self.user} had a reaction {self.date}"
        else:
            return f"{self.user} did not have a reaction {self.date}"

    class Meta:
        unique_together = ("user", "date")
