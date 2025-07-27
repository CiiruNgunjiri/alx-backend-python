from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            # Extract client IP, including proxy headers
            user_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))

            # Log token verification success with truncated token
            token = request.data.get('token', '')
            logger.info(f'Token verified successfully from IP {user_ip}: {token[:10]}...')

            # Add custom HTTP header
            response['X-Verified'] = 'true'

            return response

        except Exception as e:
            logger.warning(f'Token verification failed: {str(e)}')
            return Response({'detail': 'Token verification failed'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view to add additional user data to response
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        # Call super to get the token response
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Adjust user attribute names according to your User model
            response.data['user_id'] = getattr(user, 'user_id', user.id)
            response.data['email'] = getattr(user, 'email', '')
            # Add any other user-related data here

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that can modify the refresh response.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Add any custom data here, e.g.:
        # data['custom'] = 'some custom info'

        return Response(data, status=status.HTTP_200_OK)