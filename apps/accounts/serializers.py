from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserProfile,
    EmployeeProfile,
    EmployerProfile
)
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - handles basic user data
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model - handles user profile data
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'role',
            'phone',
            'profile_picture',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    role = serializers.ChoiceField(
        choices=UserProfile.USER_ROLES,
        required=True
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'role'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {
                    "password": "Password fields do not match."
                }
            )
        attrs.pop('password2', None)
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        """
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        if password and password.startswith('0'):
            password = '+234' + password[1:]
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user_profile = UserProfile.objects.create(user=user, role=role)
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for login - handles user authentication
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(self.user).data
        return data
        
    
