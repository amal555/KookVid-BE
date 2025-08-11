from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['user', 'avatar', 'bio']

from rest_framework import serializers
import re

class MyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        # Optional: Simple Indian mobile number validation
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError("Enter a valid Indian phone number.")
        return value

    def create(self, validated_data):
        from .utils import send_otp  # Import your send_otp utility function

        phone_number = validated_data['phone']
        result = send_otp(phone_number)

        if result['status'] == 'error':
            raise serializers.ValidationError({"error": result["message"]})

        # Optionally: store OTP to session, DB, or cache here for later verification
        return result




from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = UserProfile
        exclude = ['user']  # Don't send user in the request body



from rest_framework import serializers
from recipes.models import Recipe, Connection
from django.contrib.auth.models import User
from django.db import models

class UserProfileDetailSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    connection_count = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()
    joined_date = serializers.SerializerMethodField()
    name = serializers.CharField(source='full_name', read_only=True)
    location = serializers.CharField(source='country', read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'name',
            'email',
            'location',
            'bio',
            'username',
            'recipes_count',
            'connection_count',
            'total_views',
            'joined_date',
        ]

    def get_avatar(self, obj):
        request = self.context.get('request')
        if request and obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(created_by=obj.user).count()

    def get_connection_count(self, obj):
        return Connection.objects.filter(following=obj.user).count()

    def get_total_views(self, obj):
        return Recipe.objects.filter(created_by=obj.user).aggregate(total=models.Sum('views'))['total'] or 0

    def get_joined_date(self, obj):
        if obj.created_at:  # using created_at from UserProfile
            return obj.created_at.strftime('%Y-%m-%d')
        return None



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", required=False)
    location = serializers.CharField(source="country", required=False)
    # joined_date = serializers.DateTimeField(source="user.date_joined", read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "email",
            "bio",
            "location",
            "avatar",
        ]
        read_only_fields = [
            "username",
            "joined_date",
            "recipes_count",
            "connection_count",
            "total_views",
        ]

    def update(self, instance, validated_data):
        # Handle related User model fields (username/email)
        user_data = validated_data.pop("user", {})
        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save()

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance