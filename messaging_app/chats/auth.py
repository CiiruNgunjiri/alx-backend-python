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
            # Call the original verification logic
            response = super().post(request, *args, **kwargs)

            # Custom logic after successful verification:

            # 1. Log the successful verification
            token = request.data.get('token', '')
            user_ip = request.META.get('REMOTE_ADDR', 'unknown')
            logger.info(f'Token verified successfully from IP {user_ip}: {token[:10]}...')

            # 2. Add a custom HTTP header to the response
            response['X-Verified'] = 'true'

            # You can also add more info in the response data if you want:
            # response.data['message'] = 'Token is valid and verified successfully.'

            return response

        except Exception as e:
            # Return 401 Unauthorized if verification failed
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view to add additional user data to response
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
            serializer = TokenObtainPairSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            response.data['user_id'] = user.id
            response.data['username'] = user.username
        return response
    
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that can modify the refresh response.
    """
    def post(self, request, *args, **kwargs):
        # Call the default refresh logic
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Add any custom data here, e.g.:
        # data['custom'] = 'some custom info'

        return Response(data, status=status.HTTP_200_OK)


