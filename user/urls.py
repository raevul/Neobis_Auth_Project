from django.urls import path

from .views import RegisterAPIView, UserProfileAPIView, LoginAPIView


urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('profile/<int:user_id>/', UserProfileAPIView.as_view()),
]
