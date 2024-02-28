from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserProfileSerializer, RegisterSerializer
from .models import UserProfile


class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        user = User.objects.get(username=username)
        if user is None:
            return Response({"data": "User does not exist"})
        if not user.check_password(password):
            return Response({"data": "Incorrect password"})
        return Response({"data": "Successfully login"})


class UserProfileAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = UserProfile.objects.get(id=kwargs['user_id'])
        except UserProfile.DoesNotExist:
            return Response({"data": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

