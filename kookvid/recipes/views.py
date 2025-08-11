from rest_framework import generics, permissions
from .models import Recipe, Rating, Comment, Like, Connection
from .serializers import RatingSerializer,RecipesSerializer,ConnectionSerializer, MyRecipeSerializer ,PostCommentSerializer, CommentSerializer, LikeSerializer, RecipeDetailSerializer
from rest_framework.response import Response
from rest_framework import status,viewsets
from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import ValidationError
from .models import Recipe
from moviepy import VideoFileClip
import tempfile
from datetime import timedelta
import os


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.IsAuthenticated])
def upload_recipe(request):
    try:
        # Required fields
        title = request.data.get("title")
        description = request.data.get("description")
        category = request.data.get("category")
        difficulty = request.data.get("difficulty")
        ingredients = request.data.getlist("ingredients[]")
        video_file = request.FILES.get("video")
        thumbnail = request.FILES.get("thumbnail")
        steps = request.data.get("steps", "Cooking steps not provided.")

        # Validate required fields
        if not all([title, description, category, difficulty, video_file]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Save video temporarily to extract duration
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            for chunk in video_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            clip = VideoFileClip(tmp_file_path)
            cook_time = timedelta(seconds=int(clip.duration))
            clip.close()
        except Exception as e:
            os.remove(tmp_file_path)
            return Response({"error": f"Could not process video: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        os.remove(tmp_file_path)

        # Save the recipe
        recipe = Recipe.objects.create(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            ingredients=ingredients,
            steps=steps,
            cook_time=cook_time,
            image=thumbnail,
            video=video_file,
            created_by=request.user,
        )

        return Response({
            "message": "Recipe uploaded successfully!",
            "recipe_id": recipe.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error uploading recipe: {e}")
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
    

class RatingCreateView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



# POST /recipes/<id>/comment/
class AddCommentView(generics.CreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comment = serializer.save(user=self.request.user, recipe=recipe)
        self.full_comment = comment

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            PostCommentSerializer(self.full_comment).data,
            status=status.HTTP_201_CREATED
        )




class AddCommentReplyView(generics.CreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        parent_id = self.request.data.get('parent')

        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)

        serializer.save(user=self.request.user, recipe=recipe, parent=parent)


# GET /recipes/<id>/comments/
class ListCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        recipe = generics.get_object_or_404(Recipe, id=self.kwargs['id'])
        return Comment.objects.filter(recipe=recipe).order_by('-created_at')

# POST /recipes/<id>/like/
class LikeRecipeView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        recipe = generics.get_object_or_404(Recipe, id=self.kwargs['id'])
        like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

        if not created:
            return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Liked successfully'}, status=status.HTTP_201_CREATED)

# GET /recipes/<id>/likes/
class ListLikesView(generics.ListAPIView):
    serializer_class = LikeSerializer

    def get_queryset(self):
        recipe = generics.get_object_or_404(Recipe, id=self.kwargs['id'])
        return Like.objects.filter(recipe=recipe).order_by('-created_at')


class SingleRecipeDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        recipe = self.get_object()
        recipe.views = recipe.views + 1
        recipe.save(update_fields=["views"])
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        recipe_id = self.request.query_params.get('recipe')
        return Comment.objects.filter(recipe_id=recipe_id).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
        return Response(CommentSerializer(comment, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        comment = self.get_object()
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
        return Response(CommentSerializer(comment, context={'request': request}).data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='comment', url_name='add-comment')
    def post_comment(self, request, pk=None):
        """
        Post a comment to a specific recipe by ID (pk = recipe ID)
        """
        content = request.data.get("content")
        if not content:
            return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Recipe  # Ensure this import exists
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found."}, status=status.HTTP_404_NOT_FOUND)

        comment = Comment.objects.create(
            user=request.user,
            recipe=recipe,
            content=content
        )
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
class CommentLikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, comment_id, action):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if action == "like":
            comment.dislikes.remove(user)
            if user in comment.likes.all():
                comment.likes.remove(user)
            else:
                comment.likes.add(user)

        elif action == "dislike":
            comment.likes.remove(user)
            if user in comment.dislikes.all():
                comment.dislikes.remove(user)
            else:
                comment.dislikes.add(user)

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "likes_count": comment.likes.count(),
            "dislikes_count": comment.dislikes.count()
        }, status=status.HTTP_200_OK)


class VideoLikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, video_id, action):
        try:
            video = Recipe.objects.get(id=video_id)
        except Recipe.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if action == "like":
            video.video_dislikes.remove(user)
            if user in video.video_likes.all():
                video.video_likes.remove(user)
            else:
                video.video_likes.add(user)

        elif action == "dislike":
            video.video_likes.remove(user)
            if user in video.video_dislikes.all():
                video.video_dislikes.remove(user)
            else:
                video.video_dislikes.add(user)

        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "likes_count": video.video_likes.count(),
            "dislikes_count": video.video_dislikes.count(),
        }, status=status.HTTP_200_OK)



class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-connections')
    def my_connections(self, request):
        connections = Connection.objects.filter(follower=request.user)
        serializer = self.get_serializer(connections, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-followers')
    def my_followers(self, request):
        followers = Connection.objects.filter(following=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)


from django.contrib.auth import get_user_model
User = get_user_model()

# class ConnectUserView(APIView):
#     def post(self, request, *args, **kwargs):
#         target_user_id = request.data.get("target_user_id")

#         if not target_user_id:
#             return Response({"detail": "Target user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         if str(request.user.id) == str(target_user_id):
#             return Response({"detail": "You cannot connect to yourself."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             target_user = User.objects.get(id=target_user_id)

#             if Connection.objects.filter(follower=request.user, following=target_user).exists():
#                 return Response({"detail": "Already connected."}, status=status.HTTP_200_OK)

#             Connection.objects.create(follower=request.user, following=target_user)

#             connection_count = Connection.objects.filter(following=target_user).count()

#             return Response({
#                 "detail": "Connected successfully.",
#                 "connections": connection_count
#             }, status=status.HTTP_201_CREATED)

#         except User.DoesNotExist:
#             return Response({"detail": "Target user not found."}, status=status.HTTP_404_NOT_FOUND)



class ConnectUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):
        user = request.user
        target_user_id = request.data.get("target_user_id")

        if not target_user_id:
            return Response({"detail": "Target user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user == target_user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        connection, created = Connection.objects.get_or_create(follower=user, following=target_user)

        if not created:
            connection.delete()
            is_connected = False
        else:
            is_connected = True

        connection_count = Connection.objects.filter(following=target_user).count()

        return Response({
            "detail": "Connection updated",
            "is_connected": is_connected,
            "follower_count": connection_count
        })



@api_view(['GET'])
def similar_videos(request, video_id):
    try:
        current_video = Recipe.objects.get(id=video_id)
    except Recipe.DoesNotExist:
        return Response({"error": "Video not found"}, status=404)

    # Find up to 4 videos with same category, excluding current video
    similar = Recipe.objects.filter(
        category=current_video.category
    ).exclude(id=video_id)[:4]

    print(f"Similar videos found: {similar}")
    serializer = RecipesSerializer(similar, many=True, context={'request': request})
    return Response(serializer.data)




class MyRecipeListCreateView(generics.ListCreateAPIView):
    serializer_class = MyRecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Show all recipes or filter by logged-in user
        queryset = Recipe.objects.all().order_by('-created_at')
        if self.request.user.is_authenticated:
            # If you only want the user's own recipes, uncomment below:
            # queryset = queryset.filter(created_by=self.request.user)
            pass
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MyRecipeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MyRecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.all()

    def perform_update(self, serializer):
        # Optional: enforce that only owners can edit
        if self.request.user != self.get_object().created_by:
            raise PermissionDenied("You cannot edit this recipe.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.created_by:
            raise PermissionDenied("You cannot delete this recipe.")
        instance.delete()