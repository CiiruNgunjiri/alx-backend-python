from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from .models import Conversation, Message


class IsMessageOwner(BasePermission):
    """
    Permission to check if the user is the owner (sender or receiver) of the message.
    """

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
    Custom permission to only allow participants of a conversation to access it.
    This handles both generic permission and object permission.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # For list and create actions, allow authenticated users (you may tighten this if needed)
        if view.action in ['list', 'create']:
            return True

        # For detail actions (retrieve, update, partial_update, destroy), object permission will be checked
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Permission logic for Conversation objects
        if isinstance(obj, Conversation):
            return user in obj.participants.all()

        # Permission logic for Message objects
        if isinstance(obj, Message):
            return user in obj.conversation.participants.all()

        # Default deny
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
