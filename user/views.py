from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .serializers import (UserProfileSerializer, RegisterSerializer,
                          LoginSerilizer, LogoutSerializer, EmailVerifySerializer, TokenSerializer)
from .models import UserProfile
from .permissions import CurrentUserOrAdminOrReadOnly
from .services import send_activation_token
from .token import account_activation_token


class RegisterAPIView(APIView):
    """
    Регистрация нового пользователя.

    ---
    # Параметры
    - email: string
      - Адрес электронной почты для регистрации.
    - password: string
      - Пароль для новой учетной записи.

    # Ответ
    - message: string
      - {message: f"Выслали письмо со ссылкой для завершения регистрации на {user.email} Если письмо не пришло, не спеши ждать совиную почту - лучше проверь ящик “Спам”"}

    # Неудача
    - объязательный поля username, email, password, confirm_password
    - "username": [
        "Пользователь с таким именем уже существует."
    ],
    "email": [
        "Этот аккаунт уже зарегистирирован"
    ]
    "password": [
        "Обязательное поле."
    ]
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: 'Created', 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            send_activation_token(user, request)
            message = f"Выслали письмо со ссылкой для завершения регистрации на {user.email} Если письмо не пришло, не спеши ждать совиную почту - лучше проверь ящик “Спам”"
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyAPIView(APIView):
    """
    Подтверждение аккаунта.

    ---
    # Параметры
    - uid: string
      - Идентификатор пользователя преобразованный в строку.
    - token: string
      - Сгенерированный уникальный токен.

    # Ответ
    - message: string
      - {"message": Вы успешно потвердили свой аккаунт, теперь просим вас авторизоваться."}

    # Неудача
    - "error": "Неверный запрос"
    """
    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(id=uid)
        except Exception as e:
            user = None
            return Response({"error": "Неверный запрос"}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            message = """Вы успешно потвердили свой аккаунт, теперь просим вас авторизоваться"""
            serializer = EmailVerifySerializer({"message": message})
            return Response(serializer.data, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    """
    Авторизация пользователя.

    ---
    # Параметры
    - username: string
      - Логин пользователя для авторизации.
    - password: string
      - Созданный пароль.

    # Ответ
    - token: string
      - Сгенерированный уникальный токен для пользователя.

    # Неудача
    - "error": "Неверные учетные данные"
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerilizer,
        responses={200: 'Success', 400: 'Bad request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerilizer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileAPIView(APIView):
    """
    Профиль пользователя.

    ---
    # Параметры
    - Параметров не принимает
      - Токен который был сгенерирован при авторизации вставляется на заголовок запроса.

    # Ответ
    - id: integer
      - id пользователя
    - username: string
      - Логин пользователя.
    - email: string
      - Аккаунт пользователя.

    # Неудача
    - "error": "Профиль не найден"
    """
    permission_classes = [CurrentUserOrAdminOrReadOnly]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not found"}
    )
    def get(self, request, *args, **kwargs):
        try:
            user = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenAPIView(APIView):
    """
    Получение токена.

    ---
    # Параметры
    - Параметров не принимает

    # Ответ
    - token: string
      - Токен полученный при авторизации.

    # Неудача
    - {"error": "Токен пользователя не найден"}
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not found"}
    )
    def get(self, request, *args, **kwargs):
        token = request.auth
        if token:
            serializer = TokenSerializer({"token": token.key})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Токен пользователя не найден"}, status=status.HTTP_404_NOT_FOUND)


class LogoutAPIView(APIView):
    """
    Выход из системы.

    ---
    # Параметры
    - Параметров не принимает
      - Токен который был сгенерирован при авторизации вставляется на заголовок запроса.

    # Ответ
    - message: string
      - {"message": "Вы вышли из системы"}

    # Неудача
    - {"error": "Токен пользователя не найден"}
    - {"error": "Произошла ошибка при выходе из системы"}
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, description='Токен пользователя', type=openapi.TYPE_STRING)],
        responses={200: "Success", 400: "Bad request"}
    )
    def post(self, request, *args, **kwargs):
        token = request.query_params.get('token')

        if not token:
            return Response({"error": "Токен пользователя не найден"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request.auth.delete()
            return Response({"message": "Вы вышли из системы"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Произошла ошибка при выходе из системы"}, status=status.HTTP_400_BAD_REQUEST)
