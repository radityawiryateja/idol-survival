# Idol Survival — Backend (FastAPI + aiogram + Supabase)

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in real values
```

### Supabase table

Create a `producers` table:

```sql
create table producers (
  id uuid primary key default gen_random_uuid(),
  telegram_id bigint unique not null,
  first_name text,
  last_name text,
  username text,
  photo_url text,
  created_at timestamptz default now()
);
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

This starts the FastAPI server **and** the aiogram bot's polling loop
together (see `app/main.py`'s `lifespan` handler, which schedules
`start_bot()` as an asyncio task — it does not block the HTTP server).

## Endpoints

- `POST /api/auth/telegram-callback` — receives the Telegram Login Widget
  payload from the frontend, validates the HMAC-SHA256 signature against
  your bot token, upserts the producer row in Supabase, and returns
  `{ session_token, user }`.
- `GET /api/profile/me` — example protected endpoint. Requires
  `Authorization: Bearer <session_token>`.

## Bot

Send `/start` to your bot in Telegram to confirm the polling loop is alive.
