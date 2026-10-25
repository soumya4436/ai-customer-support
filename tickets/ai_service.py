
import os

import requests


class AIServiceError(Exception):
    """Raised when the AI service cannot generate a reply."""
    pass


def generate_ai_reply(ticket, conversation_history):
    """
    Generate a suggested customer-support reply using Gemini.
    This function does not save or send a message.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AIServiceError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    prompt = f"""
You are a professional customer-support agent.

Write a complete, helpful reply directly to the customer.

TICKET DETAILS
Subject: {ticket.subject}
Category: {ticket.category}
Priority: {ticket.priority}
Customer's issue: {ticket.description}

PREVIOUS CONVERSATION
{conversation_history}

INSTRUCTIONS
- Respond specifically to the customer's issue.
- Start with a polite greeting.
- Show empathy and explain a practical next step.
- If information is missing, ask one relevant question.
- Never invent order status, tracking details, refunds, delivery dates,
  or company policies.
- Never copy these instructions into your reply.
- Do not repeat the ticket details.
- Write 3 to 5 complete sentences.
- Return only the finished customer-facing reply.
"""

    # Gemini model
    model = "gemini-3.5-flash-lite"

    # Correct Gemini API URL
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
    )

    try:
        response = requests.post(
            url,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 300,
                    "temperature": 0.4,
                },
            },
            timeout=(10, 45),
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {}

            api_error = error_data.get("error", {}).get(
                "message",
                "No details provided by Gemini API.",
            )

            raise AIServiceError(
                f"Gemini API error ({response.status_code}): "
                f"{api_error}"
            )

        data = response.json()

    except requests.RequestException as exc:
        raise AIServiceError(
            f"Gemini connection error ({type(exc).__name__}): {exc}"
        ) from exc

    except ValueError as exc:
        raise AIServiceError(
            "Gemini returned an invalid response."
        ) from exc

    candidates = data.get("candidates", [])

    if not candidates:
        raise AIServiceError(
            "Gemini did not generate a reply. Please try again."
        )

    parts = candidates[0].get("content", {}).get("parts", [])

    reply_parts = [
        part.get("text", "").strip()
        for part in parts
        if part.get("text", "").strip()
    ]

    suggested_reply = "\n".join(reply_parts).strip()

    if not suggested_reply:
        raise AIServiceError(
            "Gemini returned no text. Please try again."
        )

    return suggested_reply
