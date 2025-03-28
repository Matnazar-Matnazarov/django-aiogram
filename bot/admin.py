from django.contrib import admin
from .models import EnglishWord, Chat


@admin.register(EnglishWord)
class EnglishWordAdmin(admin.ModelAdmin):
    list_display = ("text", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)
    list_per_page = 10


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user", "message")
    list_per_page = 10
