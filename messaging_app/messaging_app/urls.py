from django.contrib import admin
from django.urls import path, include
from chats.auth import CustomTokenObtainPairView, CustomTokenVerifyView, CustomTokenRefreshView
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, world!")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/', include('chats.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API login/logout
]

