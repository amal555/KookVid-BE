from django.contrib import admin
from .models import Recipe,Rating, Comment, Like


admin.site.register(Comment)
admin.site.register(Like)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user']

