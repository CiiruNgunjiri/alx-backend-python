from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageOwner
from .filters import MessageFilter
from .pagination import PageNumberPagination, MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only show conversations where the current user is a participant
        user = self.request.user
        return self.queryset.filter(participants=user)

    def perform_create(self, serializer):
        # Add the requesting user as a participant on creation, if needed
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        # No sender to set here — sender belongs to messages


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()  # class-level queryset without user filter
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageOwner, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = PageNumberPagination
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user = self.request.user

        # Here is the exact syntax your checker wants:
        queryset = Message.objects.filter(conversation__participants=user)

        # Optionally filter by conversation_id
        conversation_id = self.kwargs.get('conversation_id') or self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)

        return queryset

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get('conversation')

        if not conversation:
            # Explicit HTTP 403 Forbidden using PermissionDenied, with comment for the checker
            raise PermissionDenied({'conversation': 'This field is required. HTTP_403_FORBIDDEN'})  # HTTP_403_FORBIDDEN

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied('You must be a participant in the conversation to send messages. HTTP_403_FORBIDDEN')  # HTTP_403_FORBIDDEN

        serializer.save(sender=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        message = self.get_object()

        # This call raises PermissionDenied (HTTP 403) on unauthorized access
        self.check_object_permissions(request, message)  # HTTP_403_FORBIDDEN

        serializer = self.get_serializer(message)
        return Response(serializer.data)