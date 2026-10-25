# AI Customer Support

A Django-based customer-support application for creating support tickets,
viewing ticket conversations, and generating AI-assisted reply drafts.

## What this project does

The main workflow is:

1. A logged-in customer creates a ticket.
2. The ticket stores a subject, description, category, priority, status,
   customer, assigned agent, and timestamps.
3. The customer can view their own tickets in the **My Tickets** page.
4. Opening a ticket shows its conversation history.
5. The customer can add a new message to the conversation.
6. The customer can request an AI reply suggestion.
7. The AI suggestion is shown in an editable draft page. It is not saved or
   sent automatically.
8. The reviewed draft is saved as a normal conversation message only after
   the user clicks **Send Reply**.

## Project structure

```text
ai_customer_support/
├── manage.py                    # Django command-line entry point
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # Local development database
├── .env                         # Local secrets; do not commit this file
├── config/                      # Django project configuration
│   ├── settings.py              # Installed apps, database, templates, etc.
│   ├── urls.py                  # Top-level URL routes
│   ├── asgi.py                  # ASGI deployment entry point
│   └── wsgi.py                  # WSGI deployment entry point
├── tickets/                     # Main customer-support feature
│   ├── models.py                # Ticket and Message database models
│   ├── forms.py                 # Ticket and message forms
│   ├── views.py                 # Ticket pages and AI reply workflow
│   ├── urls.py                  # Ticket URL routes
│   └── ai_service.py            # Gemini API integration
├── templates/tickets/           # HTML pages for the ticket workflow
├── accounts/                    # Accounts app scaffold
├── dashboard/                   # Dashboard app scaffold
└── ai_support/                  # AI support app scaffold
```

The implemented application currently lives mainly in the `tickets` app.
The `accounts`, `dashboard`, and `ai_support` apps are registered in Django
and can be expanded later.

## Main routes

The application is served under `/tickets/`:

| URL | Purpose |
| --- | --- |
| `/tickets/new/` | Create a new ticket |
| `/tickets/my/` | List the current user's tickets |
| `/tickets/<id>/` | View a ticket and its messages |
| `/admin/` | Django admin site |

The AI suggestion and send-reply actions are submitted from the ticket pages
using Django's named URL routes.

## Requirements

- Python 3.8 or newer
- Django 4.2
- A virtual environment
- A Gemini API key for AI reply suggestions

The exact Python packages are listed in `requirements.txt`.

## Setup on Windows

Open PowerShell in the project folder:

```powershell
cd P:\ai_customer_support
```

### 1. Create a virtual environment

If the existing `venv` folder is not available, create a new one:

```powershell
python -m venv venv
```

### 2. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the following once for the current
PowerShell window and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a file named `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The project loads this value in `config/settings.py`. Never commit a real
API key to GitHub. The `.env` file is ignored by Git.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create an admin user

This is optional but useful for accessing Django admin:

```powershell
python manage.py createsuperuser
```

Follow the prompts to choose a username, email address, and password.

## Run the project

Start the Django development server:

```powershell
python manage.py runserver
```

Then open this address in a browser:

```text
http://127.0.0.1:8000/admin/
```

The project currently uses Django's admin login for authentication. After
logging in, use the ticket routes under `/tickets/`.

To stop the server, press `Ctrl+C` in the terminal.

## How the AI reply feature works

The AI workflow is implemented in `tickets/ai_service.py`:

1. The ticket subject, category, priority, description, and previous
   conversation messages are combined into a prompt.
2. The application sends that prompt to the configured Gemini model through
   the Google Generative Language API.
3. The generated text is displayed as a draft in
   `templates/tickets/ai_suggestion.html`.
4. The user can edit the draft before sending it.
5. The application saves the final text as a `Message` only after the user
   submits the send form.

If `GEMINI_API_KEY` is missing, or the API returns an error, the application
shows a readable error on the AI suggestion page.

## Useful development commands

Run Django's configuration checks:

```powershell
python manage.py check
```

Create new migrations after changing models:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Run the test suite:

```powershell
python manage.py test
```

Open a Django shell:

```powershell
python manage.py shell
```

## Git notes

The repository ignores local secrets, the virtual environment, SQLite
database changes, and Python cache files. Commit source code and dependency
files, but do not commit `.env` or API keys.

## Current limitations

- The project uses SQLite for local development.
- The custom customer/agent account workflow is not implemented yet; the
  current authentication entry point is Django admin.
- The `dashboard`, `accounts`, and `ai_support` apps are mostly scaffolding.
- AI suggestions require a valid Gemini API key and network access.
- `DEBUG` is enabled for development and must be changed before production.
