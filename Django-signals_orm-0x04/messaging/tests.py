from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class NotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username= 'senderuser',
            email = 'sender@example.com',
            first_name='senderfisrt',
            last_name = 'senderlast', 
            password='test123'
        )

        self.receiver = User.objects.create_user(
            username= 'receiveruser',
            email = 'receiver@example.com',
            first_name='receiverfisrt',
            last_name = 'receiverlast', 
            password='test123'
        )

    def test_notification_created_on_message(self):
        # Create a message from sender to receiver
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hello!')
        # Check if notification created
        notif = Notification.objects.filter(message=msg, user=self.receiver).first()
        self.assertIsNotNone(notif, "Notification was not created")
        self.assertFalse(notif.is_read, "Notification should start as unread")
