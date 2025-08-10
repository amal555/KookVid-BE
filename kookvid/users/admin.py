from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class CookeEasyAdmin(admin.ModelAdmin):
    list_display = ['user']

