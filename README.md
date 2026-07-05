# Idol Survival — Producer Dashboard

Full-stack scaffold: Vue 3 (Composition API, Vite) frontend + FastAPI
(aiogram + Supabase) backend, wired together with Telegram Login Widget
authentication.

## Folder structure

```
idol-survival/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, starts bot as bg task
│   │   ├── bot.py                # aiogram bot (/start handler, polling)
│   │   ├── config.py             # env-based settings
│   │   ├── schemas.py            # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── auth.py           # POST /api/auth/telegram-callback
│   │   │   └── protected.py      # GET  /api/profile/me (session-guarded)
│   │   └── services/
│   │       ├── telegram_auth.py  # HMAC-SHA256 widget signature check
│   │       ├── session.py        # issues/verifies JWT session tokens
│   │       └── supabase_client.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── frontend/
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── router/index.js       # route guard checks isAuthenticated()
    │   ├── lib/
    │   │   ├── api.js            # axios instance, attaches Bearer token
    │   │   ├── auth.js           # session storage helpers
    │   │   └── supabase.js       # anon-key client for direct frontend reads
    │   └── components/
    │       ├── LoginPage.vue     # loads Telegram widget, handles callback
    │       ├── TopAppBar.vue
    │       ├── BottomNav.vue
    │       └── DashboardHome.vue # converted from dashboard.html
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

## How the login flow works end to end

1. `LoginPage.vue` injects Telegram's official widget script
   (`telegram-widget.js`) with your bot's username, and defines
   `window.onTelegramAuth` as the callback.
2. When the person approves the login in Telegram, the widget calls
   `onTelegramAuth(user)` with a signed payload
   (`id`, `first_name`, `auth_date`, `hash`, …).
3. The frontend POSTs that payload as-is to
   `POST /api/auth/telegram-callback` via Axios.
4. The backend recomputes the HMAC-SHA256 hash using
   `SHA256(bot_token)` as the key and compares it to the `hash` field —
   this is what proves the data really came from Telegram and wasn't
   forged client-side.
5. On success, the backend looks up (or creates) the producer row in
   Supabase's `producers` table, issues a JWT session token, and returns
   `{ session_token, user }`.
6. The frontend stores both in `localStorage` (`lib/auth.js`) and
   redirects to the dashboard.
7. Every subsequent Axios request automatically attaches
   `Authorization: Bearer <session_token>` (see `lib/api.js`), and the
   backend's `get_current_user` dependency (`routers/protected.py`)
   verifies it before allowing access.

## Extending to the other screens

The remaining screens you shared (Idols/Contestants list, Leaderboard,
Tasks, Profile, ID Card) follow the exact same pattern as
`DashboardHome.vue`:

- Reuse `<TopAppBar>` and `<BottomNav>`.
- Convert each `<section>` block from the original HTML into scoped CSS
  + template markup on its own `.vue` file.
- Register the new route in `router/index.js`.
- Replace hard-coded numbers with an `api.get(...)` call to a matching
  FastAPI endpoint (or a direct Supabase query via `lib/supabase.js` for
  simple reads once you set up Row Level Security policies).

## Running everything locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in TELEGRAM_BOT_TOKEN, SUPABASE_URL, etc.
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`. Note: Telegram's Login Widget requires the
domain to be registered with your bot via `@BotFather` → `/setdomain`
(use a tunnel like ngrok for local testing since Telegram won't accept
plain `localhost`).
