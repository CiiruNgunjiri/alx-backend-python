from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


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
        # Create conversation and add the request user as participant automatically
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        # Only show messages in conversations where the user is a participant
        user = self.request.user
        return self.queryset.filter(conversation__participants=user)

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get('conversation')
        if not conversation:
            raise PermissionDenied({'conversation': 'This field is required.'})

        if self.request.user not in conversation.participants.all():
            raise PermissionDenied('You must be a participant in the conversation to send messages.')

        # Save message with sender set to the current user
        serializer.save(sender=self.request.user)
