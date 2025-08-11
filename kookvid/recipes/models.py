from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
import os
from tempfile import NamedTemporaryFile
from django.core.files import File
import ffmpeg
from django.db import models
from django.contrib.auth.models import User
from pathlib import Path


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    CATEGORY_CHOICES = [('Italian', 'Italian'), ('Healthy', 'Healthy'), ('Baking', 'Baking')]

    title = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.JSONField(blank=True, null=True)
    steps = models.TextField()
    cook_time = models.DurationField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='recipes/images/')
    video = models.FileField(upload_to='recipes/videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='recipes/thumbnails/', null=True, blank=True) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0) 
    video_likes = models.ManyToManyField(User, related_name="video_liked_recipes", blank=True)
    video_dislikes = models.ManyToManyField(User, related_name="video_disliked_recipes", blank=True)

    def update_counts(self):
        self.comment_count = self.comments.count()
        self.like_count = self.likes.count()
        self.dislike_count = self.dislikes.count()  
        self.save()

    def average_rating(self):
        return self.ratings.aggregate(models.Avg('stars'))['stars__avg'] or 0

    def get_upload_display(self):
        from django.utils.timesince import timesince
        return f"{timesince(self.created_at)} ago"

    def save(self, *args, **kwargs):  # ✅ Now correctly placed
        super().save(*args, **kwargs)

    @staticmethod
    def generate_video_thumbnail(video_path):
        temp_file = NamedTemporaryFile(suffix=".jpg", delete=False)
        try:
            ffmpeg.input(video_path, ss=1).output(temp_file.name, vframes=1).run(quiet=True, overwrite_output=True)
            return temp_file
        except Exception as e:
            print("Error generating thumbnail:", e)
            print(e.stderr.decode()) 
            traceback.print_exc()
            return None


    def __str__(self):
        return self.title

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    stars = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['recipe', 'user']

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"

    def is_reply(self):
        return self.parent is not None

class Like(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} liked {self.recipe.title}"

class Dislike(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')  # Prevent duplicate dislikes

    def __str__(self):
        return f"{self.user.username} disliked {self.recipe.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name="profile_following")

    def __str__(self):
        return f"Profile of {self.user.username}"

class Connection(models.Model):
    follower = models.ForeignKey(User, related_name="connection_following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="connection_followers", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'following')  # 👈 prevents duplicates

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"