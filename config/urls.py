from django.contrib import admin
from django.urls import path, include
from drf_yasg import views, openapi
from rest_framework import permissions
import os


schema_view = views.get_schema_view(
    openapi.Info(
        title="Auth API",
        default_version="v1",
        description="""In this project implemented registration, log in, logout,
        reset password, change password and username logics.
        """,
        terms_of_service="",
        contact=openapi.Contact(email=os.getenv('EMAIL')),
        license=openapi.License(name="BCD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', include('user.urls')),
]
