from django.db import models

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Returns unread messages where the user is the receiver.
        Uses `.only()` to limit retrieved fields for optimization.
        """
        return self.filter(receiver=user, read=False).only('message_id', 'sender', 'content', 'sent_at')
