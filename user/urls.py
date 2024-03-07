from django.urls import path

from .views import (RegisterAPIView, UserProfileAPIView, LoginAPIView,
                    LogoutAPIView, EmailVerifyAPIView, GetTokenAPIView)


urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('verify_email/<str:uid64>/<str:token>/', EmailVerifyAPIView.as_view(), name='verify_email'),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('token/', GetTokenAPIView.as_view()),
    path('profile/', UserProfileAPIView.as_view()),
]
