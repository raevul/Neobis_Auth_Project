from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .serializers import UserProfileSerializer, RegisterSerializer
from .models import UserProfile
from .permissions import CurrentUserOrAdminOrReadOnly
from .services import send_activation_token
from .token import account_activation_token


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            send_activation_token(user, request)
            message = f"""Выслали письмо со ссылкой для завершения регистрации на {user.email}
                          Если письмо не пришло, не спеши ждать совиную почту - лучше проверь ящик “Спам” """
            content = {
                message: serializer.data,
            }
            return Response(content, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyAPIView(APIView):
    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(id=uid)
        except Exception as e:
            user = None
            return Response({"data": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            message = """Вы успешно потвердили свой аккаунт, теперь просим вас залогинится"""
            return Response({"data": message}, status=status.HTTP_200_OK)


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
            return Response({"data": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"data": "Вы вышли из системы"}, status=status.HTTP_200_OK)
