from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'This profile is {self.username}'
