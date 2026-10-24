from django.contrib import admin
from .models import Ticket, Message


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "customer",
        "category",
        "priority",
        "status",
        "created_at",
    )

    list_filter = ("category", "priority", "status")

    search_fields = (
        "subject",
        "description",
        "customer__username",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "sender",
        "created_at",
    )

    search_fields = (
        "body",
        "sender__username",
        "ticket__subject",
    )