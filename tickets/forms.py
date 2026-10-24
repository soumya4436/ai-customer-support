from django import forms
from .models import Ticket,Message


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            "subject",
            "description",
            "category",
            "priority",
        ]

        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your problem title",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Explain your problem...",
                "rows": 5,
            }),

            "category": forms.Select(attrs={
                "class": "form-select",
            }),

            "priority": forms.Select(attrs={
                "class": "form-select",
            }),
        }


from .models import Message


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ["body"]

        widgets = {
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Type your message...",
                "rows": 3,
            }),
        }