from django.contrib import admin
from .models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "full_name",
        "phone_number",
        "telegram_link",
        "created_at",
        "role",
    )
    list_filter = ("role", "created_at")
    search_fields = ("telegram_id", "username", "full_name", "phone_number")
    list_per_page = 10
    list_editable = ("role",)
    list_display_links = ("telegram_id", "username", "full_name", "phone_number")
