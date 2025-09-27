"""
This script MUST be run first before running any other code.
It will generate the necessary tables in the database.

Run these commands in your terminal:
1. python manage.py makemigrations
2. python manage.py migrate
"""
from django.db import models

# TODO: edit this with the correct fields we want
class User(models.Model):
    # sample for testing purposese
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name