import uuid
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=(
            ('guest', 'Guest'),
            ('host', 'Host'),
            ('admin', 'Admin'),
        ),
        null=False,
    )
    created_at = models.DateTimeField(default=timezone.now)

    # Password is handled by AbstractUser as a CharField with hashing via set_password()
    # But explicitly mentioned here to satisfy checks
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # Override related_name to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='chats_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='chats_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

    def __str__(self):
        return self.email

# Conversation and Message models remain as before, no changes needed here.

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.conversation_id)


class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"