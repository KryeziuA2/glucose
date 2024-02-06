# models.py

from django.db import models
from django.contrib.auth.models import User

class GlucoseReading(models.Model):
    BEFORE_EATING = 'before'
    AFTER_EATING = 'after'
    READING_CHOICES = [
        (BEFORE_EATING, 'Before Eating'),
        (AFTER_EATING, 'After Eating'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reading = models.DecimalField(max_digits=5, decimal_places=2)
    date_time = models.DateTimeField()
    reading_type = models.CharField(max_length=6, choices=READING_CHOICES, default=BEFORE_EATING)

    def __str__(self):
         return f"{self.user.username} - {self.reading} ({self.get_reading_type_display()}) at {self.date_time}"

class Food(models.Model):
    name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    carbohydrates = models.PositiveIntegerField()
    proteins = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()

class Chat(models.Model):
    message = models.TextField()
    response = models.TextField()
    def __str__(self):
        return self.name

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foods = models.ManyToManyField(Food)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s Meal on {self.date}"
