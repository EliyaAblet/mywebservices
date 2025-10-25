from django.db import models
from django.contrib.auth.models import User

class Dog(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    breed = models.CharField(max_length=100)

    def __str__(self):
        return self.name

