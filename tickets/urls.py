from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("new/", views.create_ticket, name="create_ticket"),
    path("my/", views.my_tickets, name="my_tickets"),
    path(
        "<int:ticket_id>/",
        views.ticket_detail,
        name="ticket_detail",
    ),
]