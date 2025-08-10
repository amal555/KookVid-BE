from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    CULINARY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]

    CUISINE_CHOICES = [
        ('indian', 'Indian'),
        ('italian', 'Italian'),
        ('chinese', 'Chinese'),
        ('mexican', 'Mexican'),
        ('other', 'Other'),
    ]

    COOKING_EXPERIENCE_CHOICES = [
        ('<1', 'Less than 1 year'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5+', 'More than 5 years'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)  
    country = models.CharField(max_length=100, blank=True, null=True)  
    full_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bio = models.TextField(blank=True)
    culinary_level = models.CharField(max_length=20, choices=CULINARY_LEVEL_CHOICES, blank=True)
    favorite_cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES, blank=True)
    cooking_experience = models.CharField(max_length=10, choices=COOKING_EXPERIENCE_CHOICES, blank=True)

    # ✅ New fields for tracking join and update times
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # set once at creation
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)      # updates every save

    def __str__(self):
        return self.username or self.user.username


