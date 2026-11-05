from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Recipe(models.Model):
    title=models.CharField(max_length=100)
    cuisine=models.CharField(max_length=50)
    cooking_time=models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1440)
    ])
    servings=models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)

    ])
    ingredients=models.TextField()
    instructions=models.TextField()
