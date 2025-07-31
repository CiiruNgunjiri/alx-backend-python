from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL  # Supports custom user model if any

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        # Returns unread messages where the user is the receiver
        # Use `.only()` to select only necessary fields to optimize query
        return self.filter(receiver=user, read=False).only('message_id', 'sender', 'content', 'sent_at')
    
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messaging_sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messaging_received_messages')
    conversation = models.ForeignKey('chats.Conversation', on_delete=models.CASCADE, related_name='messaging_messages', null=True, blank=True)
    content = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)  # Set current time on create
    sent_at = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)  # New field to track if message is read

     # NEW: Parent message for threading (nullable, since not every message is a reply)
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

     # Default manager
    objects = models.Manager()

    # Custom manager for unread messages
    unread = UnreadMessagesManager()

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver} at {self.sent_at}'

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user} about message {self.message.id}'

class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='edit_history'
    )
    old_message_body = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit of Message {self.message.message_id} at {self.edited_at}"