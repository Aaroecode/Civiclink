# Civiclink

Civiclink is a WhatsApp-based road issue reporting assistant. Users can seamlessly report road infrastructure issues (such as potholes, damaged roads, and drainage problems) by chatting with a WhatsApp bot, sharing images, and providing their location.

## Features
- **Multi-language Support:** Users can interact in English, Hindi, Telugu, Tamil, or Punjabi.
- **AI-Powered Issue Detection:** Automatically analyzes user-submitted images using OpenAI to detect road infrastructure issues.
- **Location Tracking:** Captures user location to map out the exact location of the issue.
- **Ticketing System:** Generates a unique ticket for every reported issue and tracks its status via Elasticsearch.

## Tech Stack
- **FastAPI:** Backend web framework.
- **Elasticsearch:** Used for storing user sessions, user data, and reported tickets.
- **WhatsApp Cloud API:** Handles the incoming and outgoing WhatsApp messages.
- **OpenAI (GPT-4o):** For processing images and identifying the road issues.

## Prerequisites
- Python 3.9+
- Elasticsearch instance running locally or remotely (with `http_ca.crt` placed in `database/` for local secure connections).
- WhatsApp Cloud API Developer Account and access token.
- OpenAI API Key.

## Setup Instructions

1. **Clone the repository and navigate into it.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup:**
   Copy the `.env.example` file to `.env` and fill in your credentials.
   ```bash
   cp .env.example .env
   ```
4. **Elasticsearch Configuration:**
   Ensure you have Elasticsearch running on `https://127.0.0.1:9200`. Put your CA certificate in `database/http_ca.crt` and a JSON array `[]` inside `database/uuids.json` if it doesn't exist, and an empty JSON object `{}` in `database/languages.json`.
5. **Start the application:**
   ```bash
   python main.py
   ```
   The API will be available at `http://127.0.0.1:8082`.

## Webhook Configuration
Configure your WhatsApp App Dashboard to use the following Webhook URL:
- **Callback URL:** `https://your-domain.com/` (Make sure to expose your local server using a tool like ngrok if testing locally).
- **Verify Token:** `tensorlabz` (Configured in `api/v1/webhook.py`).

## API Endpoints Overview
- `GET /`: Webhook verification.
- `POST /`: Webhook to receive incoming WhatsApp messages.
- `GET /data`: Exposes ticket data from Elasticsearch.
- `POST /login`, `POST /create_user`: Authentication routes.
- `GET /images/{filename}`: Serve locally downloaded images.
