from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
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
        # Show only conversations where the user is a participant
        user = self.request.user
        return self.queryset.filter(participants=user)

    def perform_create(self, serializer):
        # Automatically add the creator as a participant when creating a conversation
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
        # Show only messages from conversations where the user is a participant
        user = self.request.user
        return self.queryset.filter(conversation__participants=user)

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get('conversation')
        if not conversation:
            raise ValidationError({'conversation': 'This field is required.'})

        # Check participant permission on the conversation
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied('You must be a participant in the conversation to send messages.')

        serializer.save(sender=self.request.user)
