from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet
from chats.auth import CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    # JWT Authentication endpoints (usually prefixed with 'api/token/')
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),

    # Browsable API login/logout (optional)
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework_auth')),

    # Main API routes
    path('api/', include(router.urls)),
    path('api/', include(conversations_router.urls)),
]
