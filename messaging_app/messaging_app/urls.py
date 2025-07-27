from django.contrib import admin
from django.urls import path, include
from chats.auth import CustomTokenObtainPairView, CustomTokenVerifyView, CustomTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API login/logout
]

