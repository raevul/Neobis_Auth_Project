from django.urls import path

from .views import RegisterAPIView, UserProfileAPIView, LoginAPIView, LogoutAPIView


urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('profile/', UserProfileAPIView.as_view()),
]
