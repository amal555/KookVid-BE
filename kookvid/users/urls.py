from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, ProfileView, send_otp,SendOTPView, UserProfileDetailView, VerifyOTPView, UserProfileCreateView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', obtain_auth_token),
    # path('profile/', ProfileView.as_view()),
    path("auth/send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path('profile/create/', UserProfileCreateView.as_view(), name='create-profile'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
]

