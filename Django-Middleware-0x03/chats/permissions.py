from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from .models import Conversation, Message
from rest_framework import permissions


class IsMessageOwner(BasePermission):
    """
    Permission to check if the user is the owner (sender or receiver) of the message.
    """
    message = 'You must be the sender of this message.'

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Only sender or receiver can access the message
        return obj.sender == user or obj.receiver == user


class IsConversationParticipant(BasePermission):
    """
    Permission to check if the user is part of the conversation participants.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # User must be in participants to access the conversation object
        return user in obj.participants.all()


class IsParticipantOfConversation(BasePermission):
    """
    Allow only participants of a conversation to send, view, update, or delete messages.
    """
    message = 'You must be a participant of this conversation.'

    def has_permission(self, request, view):
        # Only allow authenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        # For list or create actions, allow authenticated users (assuming participant checks happen at object-level)
        if view.action in ['list', 'create']:
            return True

        # For retrieve, update, partial_update, delete, allow and defer to `has_object_permission`
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Check participant access for Conversation object
        if isinstance(obj, Conversation):
            return user in obj.participants.all()

        # Check participant access for Message object by verifying user is participant in related conversation
        if isinstance(obj, Message):
            # For read-only operations (GET, HEAD, OPTIONS), allow participants
            if request.method in SAFE_METHODS:
                return user in obj.conversation.participants.all()
            
            # For unsafe methods (PUT, PATCH, DELETE), allow only if user is participant
            if request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
                return user in obj.conversation.participants.all()

        # Deny by default
        return False

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners to read or edit their own messages or conversations.
    Read-only for others.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Allow read-only methods (GET, HEAD, OPTIONS) for all authenticated users
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # Assumes object has `user` attribute pointing to owner
        return obj.user == user