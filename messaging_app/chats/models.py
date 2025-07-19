import uuid
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=[
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin')
    ], blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Override username and email behavior
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # Avoid reverse accessor clashes by redefining related_name for these fields:
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
        return f'Message from {self.sender.email} at {self.sent_at}'
