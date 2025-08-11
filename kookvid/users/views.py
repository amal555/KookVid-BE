from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegisterSerializer, ProfileSerializer,UserProfileUpdateSerializer, UserProfileDetailSerializer, UserProfileSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from twilio.rest import Client
import random
from django.core.cache import cache
from rest_framework.decorators import action
# from .models import Connection
from rest_framework import viewsets, permissions
from rest_framework import generics, permissions

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user.userprofile)
        return Response(serializer.data)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_otp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import MyOTPSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SendOTPView(APIView):
    def post(self, request):
        serializer = MyOTPSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import UserProfile
User = get_user_model()


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        otp = request.data.get("otp")

        if not phone or not otp:
            return Response({"message": "Phone and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Dummy OTP check — Replace with actual OTP logic from DB or cache
        if otp != "123456":
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create or get user & profile
        profile = UserProfile.objects.filter(phone=phone).first()

        if profile:
            user = profile.user
        else:
            user = User.objects.create(username=phone)
            profile = UserProfile.objects.create(user=user, phone=phone)

        # ✅ Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "phone": profile.phone,
                "username": user.username,
            }
        }, status=status.HTTP_200_OK)




class UserProfileCreateView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Extract username from request body (if provided)
        username = self.request.data.get("username")

        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults=serializer.validated_data
        )

        if not created:
            for field, value in serializer.validated_data.items():
                setattr(profile, field, value)
            profile.save()

        # Update the username in User model if provided
        if username:
            self.request.user.username = username
            self.request.user.save()




class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # ✅ If UserProfile has OneToOneField to User
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = UserProfileDetailSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)