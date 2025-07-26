from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Conversation, Message

class IsMessageOwner(BasePermission):
    """
    Permission to check if the user is the owner of the message
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the sender or receiver of the message
        return obj.sender == request.user or obj.receiver == request.user

class IsConversationParticipant(BasePermission):
    """
    Permission to check if the user is part of the conversation
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is one of the participants
        return request.user in obj.participants.all()
    
class IsParticipantOfConversation(IsAuthenticated):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
            
        # For list/create views
        if view.action in ['list', 'create']:
            return True
            
        # For retrieve/update/destroy, check object permission
        return True

    def has_object_permission(self, request, view, obj):
        # Handle Conversation objects
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
            
        # Handle Message objects
        if isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
            
        return False