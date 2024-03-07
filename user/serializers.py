from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8, max_length=15)
    confirm_password = serializers.CharField(write_only=True, min_length=8, max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')
        if password != confirm_password:
            raise ValidationError({"data": "Пароли не совпадают"})
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise ValidationError({"data": "Этот аккаунт уже зарегистирирован"})

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, username=user.username, email=user.email)
        return user


class LoginSerilizer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8, max_length=15)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise ValidationError("Введите имя пользователя и пароль")
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Чтобы авторизоваться нужно потвердить аккаунт")
        user.save()
        return {'username': username, 'password': password}


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()


class EmailVerifySerializer(serializers.Serializer):
    message = serializers.CharField()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
