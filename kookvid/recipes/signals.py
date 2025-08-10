from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()




from django.db.models.signals import post_save
from django.dispatch import receiver
from pathlib import Path
from django.core.files import File  # ✅ Add this import
from .models import Recipe

@receiver(post_save, sender=Recipe)
def generate_thumbnail_after_save(sender, instance, created, **kwargs):
    print("Signal fired")
    if instance.video and not instance.thumbnail:
        video_path = Path(instance.video.path)
        if video_path.exists():
            thumbnail_file = instance.generate_video_thumbnail(video_path)
            if thumbnail_file:
                thumbnail_name = f"{video_path.stem}.jpg"
                instance.thumbnail.save(thumbnail_name, File(thumbnail_file), save=True)