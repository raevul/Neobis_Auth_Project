from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login

from .serializers import UserProfileSerializer, RegisterSerializer, LoginSerializer
from .models import UserProfile
from .permissions import CurrentUserOrAdminOrReadOnly


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            token = Token.objects.get(user=account)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return Response({'data': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        token = Token.objects.get(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    permission_classes = [CurrentUserOrAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"data": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"data": "You are logged out"}, status=status.HTTP_200_OK)
