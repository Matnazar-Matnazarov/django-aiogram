from django.db import models
from accounts.models import CustomUser
from django.utils import timezone
from asgiref.sync import sync_to_async


# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name="User",
        null=True,
        blank=True,
    )
    message_data = models.JSONField(
        verbose_name="Message data", null=True, blank=True, default=list
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}"

    def add_message(self, text: str):
        if not isinstance(self.message_data, list):
            self.message_data = []

        self.message_data.append(
            {
                "text": text,
                "time": timezone.now().isoformat(),
            }
        )
        self.save()

    def get_messages(self, limit: int = None):
        messages = self.message_data or []
        if limit:
            messages = messages[-limit:]
        return messages

    def clear_messages(self):
        self.message_data = []
        self.save()

    @sync_to_async
    def async_add_message(self, text: str):
        """Async version of add_message"""
        self.add_message(text)

    @sync_to_async
    def async_get_messages(self, limit: int = None):
        """Async version of get_messages"""
        return self.get_messages(limit)

    @sync_to_async
    def async_clear_messages(self):
        """Async version of clear_messages"""
        self.clear_messages()


class EnglishWord(models.Model):
    text = models.CharField(
        max_length=255,
        verbose_name="Text",
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
