from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Food(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# class UserFood(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     food = models.ForeignKey(Food, on_delete=models.CASCADE)
#     # reactivity = models.PositiveIntegerField()

#     def __str__(self):
#         return f"{self.user.username} {self.food.name} {self.reactivity}"

#     def get_reactivity(self):
#         # get meals and reactions for the user
#         #
#         # for reaction in reactions:
#         #   if meal.date is day_before:
#         #       reactivity += 1
#         pass


class Meal(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="user"
    )
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.PositiveIntegerField()

    def get_absolute_url(self):
        return reverse("dashboard")

    def __str__(self):
        return f"{self.user} ate {self.amount}g of {self.food} {self.date}"


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
        return reverse("dashboard")

    def __str__(self):
        if self.reaction:
            return f"{self.user} had a reaction {self.date}"
        else:
            return f"{self.user} did not have a reaction {self.date}"

    class Meta:
        unique_together = ("user", "date")
