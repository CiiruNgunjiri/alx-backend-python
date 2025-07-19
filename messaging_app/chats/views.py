from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Chats Home Page!")

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        sender_id = request.data.get('sender')
        conversation_id = request.data.get('conversation')
        if not sender_id or not conversation_id:
            return Response({'detail': 'sender and conversation fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        sender = get_object_or_404(User, pk=sender_id)
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        if sender not in conversation.participants.all():
            return Response({'detail': 'Sender must be a participant in the conversation'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=sender, conversation=conversation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
