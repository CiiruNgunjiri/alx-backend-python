from django.contrib import admin
from django.urls import path, include
from chats.auth import CustomTokenObtainPairView, CustomTokenVerifyView, CustomTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    
    path('api/', include('chats.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API login/logout
]

