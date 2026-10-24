from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TicketForm, MessageForm
from .models import Ticket, Message

@login_required
def create_ticket(request):

    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.customer = request.user
            ticket.save()

            messages.success(
                request,
                f"Ticket #{ticket.pk} created successfully!"
            )

            return redirect("tickets:my_tickets")

    else:
        form = TicketForm()

    return render(
        request,
        "tickets/create_ticket.html",
        {"form": form},
    )


@login_required
def my_tickets(request):

    tickets = Ticket.objects.filter(
        customer=request.user
    ).order_by("-created_at")

    return render(
        request,
        "tickets/my_tickets.html",
        {"tickets": tickets},
    )

@login_required
def ticket_detail(request, ticket_id):

    # Find a ticket owned by the logged-in customer.
    ticket = get_object_or_404(
        Ticket,
        pk=ticket_id,
        customer=request.user,
    )

    # Load the messages belonging to this ticket.
    ticket_messages = ticket.messages.select_related(
        "sender"
    ).all()

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()

            messages.success(
                request,
                "Your message has been sent successfully!",
            )

            return redirect(
                "tickets:ticket_detail",
                ticket_id=ticket.pk,
            )

    else:
        form = MessageForm()

    context = {
        "ticket": ticket,
        "ticket_messages": ticket_messages,
        "form": form,
    }

    return render(
        request,
        "tickets/ticket_detail.html",
        context,
    )