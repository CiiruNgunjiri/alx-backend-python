from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.core.exceptions import ObjectDoesNotExist
from chats.models import User
from django.conf import settings

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        # When a new message is created, generate notification for receiver
        Notification.objects.create(user=instance.receiver, message=instance)

def log_message_edit(sender, instance, **kwargs):
    """
    Before saving a message, check if it already exists.
    If it exists and the message_body has changed, save the old content in MessageHistory.
    """
    if not instance.pk:
        # New message, no history to log
        return

    try:
        old_instance = Message.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        # Message does not exist in DB yet
        return
    
    if old_instance.message_body != instance.message_body:
        # Message content has changed: log previous content
        MessageHistory.objects.create(
            message=instance,
            old_message_body=old_instance.message_body,
        )
        # Mark message as edited
        instance.edited = True

@receiver(post_delete, sender=User)
def delete_related_user_data(sender, instance, **kwargs):
    """
    Cleans up messages, notifications, and message histories related to a user after the user is deleted.
    """
    # Delete Messages related to the user either sent or received.
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete Notifications for the user
    Notification.objects.filter(user=instance).delete()

    # Delete MessageHistory that links to messages of the deleted user
    # First delete message histories related to messages from the deleted user
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()