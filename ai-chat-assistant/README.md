# Nova — AI Chat Assistant

A full-stack AI chat application built with **React + Vite**, **Python FastAPI**, **Supabase PostgreSQL**, and streaming integration with **OpenAI or Anthropic Claude**.

## Original problem statement

Build a complete functional AI chat assistant using a React frontend, Python FastAPI backend, a database, OpenAI or Claude API integration, and Server-Sent Events (SSE) for streaming responses. The application provides separate user and AI message bubbles, a scrollable conversation window, progressively streamed AI responses, a sidebar of previous conversations, persistent conversation IDs and timestamps, and professional/casual/concise tone selection passed to the model through a backend system instruction. It also supports regenerating and copying AI responses. All business logic, validation, and computations live in FastAPI; the frontend handles presentation and user interactions. API keys and database credentials remain in backend environment variables and are never exposed to frontend code.

## Features

- Create, browse, and reopen saved conversations.
- Separate user and assistant message bubbles in a scrollable chat.
- Stream AI response text over Server-Sent Events.
- Select Professional, Casual, or Concise tone; FastAPI passes the corresponding system instruction to the model.
- Regenerate the latest assistant response and copy assistant messages.
- Persist conversation IDs, titles, timestamps, message roles, prompts, and responses in Supabase PostgreSQL.
- Choose OpenAI or Anthropic Claude through backend environment configuration.
- Responsive React interface, loading indicators, request validation, and user-facing errors.

## Architecture

```text
React (Vite)
  ├── Sidebar / ChatWindow / MessageBubble / ToneSelector
  └── Fetch API + ReadableStream (SSE)
            |
            v
FastAPI
  ├── routes/chat.py           HTTP endpoints and SSE responses
  ├── schemas/chat.py          Pydantic request validation
  ├── services/chat_service.py Supabase conversation/message operations
  ├── services/ai_service.py   OpenAI / Anthropic adapter + tone instructions
  ├── config.py                Backend environment configuration
  └── database.py              Supabase client lifecycle
            |                         |
            v                         v
     Supabase PostgreSQL        OpenAI / Claude API
```

The browser communicates only with FastAPI. Supabase and model-provider credentials are stored in `backend/.env`; no secret is placed in frontend code.

## Requirements

- Python 3.10+
- Node.js 18+
- A Supabase project
- An OpenAI API key or Anthropic API key

## Supabase setup

1. Create a project at https://supabase.com/dashboard.
2. In **SQL Editor**, run the SQL in `backend/database/schema.sql` (if the tables have already been created, do not run a second copy unnecessarily; the statements are safe with `IF NOT EXISTS`).
3. Open **Project Settings → API Keys** and copy the Project URL and a backend secret key. A legacy `service_role` key also works.
4. Keep the secret key private. It must never be used in React or committed to Git.

## Setup and run

Open separate terminals from the project root.

### 1. Configure and start FastAPI

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`:

```env
FRONTEND_ORIGIN=http://localhost:5173
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_SECRET_KEY

LLM_PROVIDER=openai
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4o-mini
```

For Claude instead, set `LLM_PROVIDER=anthropic` and provide `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`.

Start the API from the `backend` directory:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs  
Health check: http://localhost:8000/api/health

### 2. Start React

In a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | API and Supabase health |
| `POST` | `/api/chats` | Create a conversation |
| `GET` | `/api/chats` | List recent conversations |
| `GET` | `/api/chats/{conversation_id}` | Load a conversation and messages |
| `POST` | `/api/chats/{conversation_id}/messages` | Save user prompt and stream a response |
| `POST` | `/api/chats/{conversation_id}/regenerate` | Regenerate the latest assistant response |

## Tests

From the `backend` directory:

```powershell
pytest -q
```

The included schema tests cover valid messages, empty prompts, and invalid tone values. For live testing, configure Supabase and a valid model API key, start the API and frontend, then test creating a conversation, sending a prompt, refreshing/reopening history, switching tones, copying, and regenerating.

## Security and limitations

- This starter does not include user accounts or per-user authorization. The backend secret/service-role key grants privileged database access; keep the API local or add authentication, authorization, rate limiting, HTTPS, and deployment-specific CORS before exposing it publicly.
- Never commit `backend/.env`. The repository `.gitignore` excludes environment files and virtual environments.
- User prompts are saved before model generation. If generation fails, the prompt remains in conversation history and the UI displays an error.
