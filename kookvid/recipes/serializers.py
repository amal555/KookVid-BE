from rest_framework import serializers
from .models import Recipe, Rating, Comment, Like, Connection

# class RecipeSerializer(serializers.ModelSerializer):
#     average_rating = serializers.FloatField(read_only=True)

#     class Meta:
#         model = Recipe
#         fields = '__all__'
#         read_only_fields = ['created_by', 'created_at']

class RecipesSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'video', 'thumbnail','duration', 'views', 'author', 'category', 'difficulty']

    def get_video(self, obj):
        request = self.context.get('request')
        if request and obj.video:
            return request.build_absolute_uri(obj.video.url)
        return None

    def get_duration(self, obj):
        total_seconds = int(obj.cook_time.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"

    def get_views(self, obj):
        return "650K views"

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        if request and obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_author(self, obj):
        return obj.created_by.username if obj.created_by else "Unknown"

        
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source='text')
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'likes', 'dislikes']
        read_only_fields = ['id', 'user', 'created_at', 'likes', 'dislikes']

    def get_user(self, obj):
        return obj.user.username  # or obj.user.email or obj.user.id, etc.

    def get_likes(self, obj):
        return obj.likes.count()

    def get_dislikes(self, obj):
        return obj.dislikes.count()

class CommentSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    content = serializers.CharField(source='text', read_only=True)
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'recipe', 'created_at',
            'likes', 'dislikes', 'parent', 'replies'
        ]

    def get_likes(self, obj):
        return obj.likes.count()

    def get_dislikes(self, obj):
        return obj.dislikes.count()

    def get_author(self, obj):
        return obj.user.username if obj.user else "Unknown"

    def get_replies(self, obj):
        replies = obj.replies.all().order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']


class RecipeDetailSerializer(serializers.ModelSerializer):
    uploadDate = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id", "title", "video", "thumbnail", "duration", "views", "author", "category",
            "difficulty", "description", "ingredients", "uploadDate", "likes", "dislikes"
        ]

    def get_uploadDate(self, obj):
        return obj.get_upload_display()

    def get_video(self, obj):
        request = self.context.get('request')
        if request and obj.video:
            return request.build_absolute_uri(obj.video.url)
        return None

    def get_likes(self, obj):
        return obj.video_likes.count()

    def get_dislikes(self, obj):
        return obj.video_dislikes.count()

    def get_duration(self, obj):
        if not obj.cook_time:
            return "0:00"
        total_seconds = int(obj.cook_time.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"

    def get_views(self, obj):
        views = obj.views
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M views"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K views"
        return f"{views} views"

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        if request and obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


    def get_author(self, obj):
        user = obj.created_by
        request = self.context.get('request')
        viewer = request.user if request else None

        if not user:
            return {"username": "Unknown"}
        # breakpoint()
        # Get follower count and check if viewer follows this author
        follower_count = Connection.objects.filter(following=user).count()
        is_connected = False
        if viewer and viewer.is_authenticated:
            is_connected = Connection.objects.filter(follower=viewer, following=user).exists()

        return {
            "id": user.id,
            "username": user.username,
            "follower_count": follower_count,
            "is_connected": is_connected,
        }


from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ConnectionSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = ['id', 'follower', 'following', 'created_at']



class MyRecipeSerializer(serializers.ModelSerializer):
    uploadDate = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    likes = serializers.IntegerField(source="like_count", read_only=True)
    status = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = [
            "id", "title", "thumbnail","video", "duration", "views",
            "category", "difficulty", "status", "uploadDate", "likes"
        ]

    def get_uploadDate(self, obj):
        return obj.get_upload_display() 

    def get_duration(self, obj):
        # Convert timedelta to mm:ss or hh:mm:ss
        total_seconds = int(obj.cook_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"

    def get_status(self, obj):
        # You can adjust this if you have a "status" field
        return "published"

    def get_video(self, obj):
        request = self.context.get('request')
        if request and obj.video:
            return request.build_absolute_uri(obj.video.url)
        return None