from django.urls import path
from .views import RecipeListCreateView, upload_recipe, similar_videos,MyRecipeListCreateView,MyRecipeRetrieveUpdateDestroyView, ConnectUserView, SingleRecipeDetailView, VideoLikeDislikeView, CommentLikeDislikeView, AddCommentReplyView, RatingCreateView,AddCommentView, ListCommentsView, LikeRecipeView, ListLikesView

from rest_framework.routers import DefaultRouter
from .views import CommentViewSet
from .views import ConnectionViewSet

router = DefaultRouter()
router.register(r'connections', ConnectionViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = router.urls

urlpatterns = [
    path('' , RecipeListCreateView.as_view()),
    path("<int:id>/detail/", SingleRecipeDetailView.as_view()),
    path('<int:pk>/rate/', RatingCreateView.as_view()),
    path("upload_receipe", upload_recipe, name="upload_recipe"),
    path('recipes/<int:id>/comment/', AddCommentView.as_view(), name='add-comment'),
    path('recipes/<int:id>/comments/', ListCommentsView.as_view(), name='list-comments'),
    path('recipes/<int:id>/like/', LikeRecipeView.as_view(), name='like-recipe'),
    path('recipes/<int:id>/likes/', ListLikesView.as_view(), name='list-likes'),
    path('recipes/<int:id>/reply/comment/', AddCommentReplyView.as_view(), name='add_reply_comment'),
    path("comment/<int:comment_id>/<str:action>/", CommentLikeDislikeView.as_view(), name="comment-like-dislike"),
    path("video/<int:video_id>/<str:action>/", VideoLikeDislikeView.as_view(), name="video-like-dislike"),
    path('connect/', ConnectUserView.as_view(), name='connect-user'),
    path('<int:video_id>/similar/', similar_videos, name='similar-videos'),
    path("myrecipes/", MyRecipeListCreateView.as_view(), name="recipe-list-create"),
    path("recipes/<int:pk>/", MyRecipeRetrieveUpdateDestroyView.as_view(), name="recipe-detail"),
]
