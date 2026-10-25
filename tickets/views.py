
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import TicketForm, MessageForm
from .models import Ticket, Message
from .ai_service import AIServiceError, generate_ai_reply


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
                f"Ticket #{ticket.pk} created successfully!",
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
    # Only allow the logged-in customer to access their own ticket.
    ticket = get_object_or_404(
        Ticket,
        pk=ticket_id,
        customer=request.user,
    )

    ticket_messages = ticket.messages.select_related(
        "sender"
    ).order_by("created_at")

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


@login_required
@require_POST
def suggest_ai_reply(request, ticket_id):
    # Only allow the logged-in customer to request a draft
    # for their own ticket.
    ticket = get_object_or_404(
        Ticket,
        pk=ticket_id,
        customer=request.user,
    )

    # Read existing messages in chronological order.
    ticket_messages = ticket.messages.select_related(
        "sender"
    ).order_by("created_at")

    conversation_history = "\n".join(
        f"{message.sender.username}: {message.body}"
        for message in ticket_messages
    )

    try:
        # Generate a draft. This function should not save or send it.
        suggested_reply = generate_ai_reply(
            ticket,
            conversation_history,
        )

        return render(
            request,
            "tickets/ai_suggestion.html",
            {
                "ticket": ticket,
                "suggested_reply": suggested_reply,
                "error": None,
            },
        )

    except AIServiceError as exc:
        # Display a handled AI error on the suggestion page.
        return render(
            request,
            "tickets/ai_suggestion.html",
            {
                "ticket": ticket,
                "suggested_reply": None,
                "error": str(exc),
            },
        )


@login_required
@require_POST
def send_ai_reply(request, ticket_id):
    """
    Save the reviewed AI reply as a conversation message.
    The reply is saved only after the user submits the form.
    """

    # Only allow the logged-in customer to access their own ticket.
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        customer=request.user,
    )

    # Get the edited reply from the form.
    body = request.POST.get("body", "").strip()

    # Validate the reply.
    if not body:
        messages.error(request, "Reply cannot be empty.")
        return redirect(
            "tickets:ticket_detail",
            ticket_id=ticket.id,
        )

    if len(body) > 10000:
        messages.error(
            request,
            "Reply is too long. Please keep it under 10,000 characters.",
        )
        return redirect(
            "tickets:ticket_detail",
            ticket_id=ticket.id,
        )

    # Save the reply only after the form is submitted.
    Message.objects.create(
        ticket=ticket,
        sender=request.user,
        body=body,
    )

    messages.success(request, "Your reply was sent successfully.")

    # Return to the ticket conversation.
    return redirect(
        "tickets:ticket_detail",
        ticket_id=ticket.id,
    )
