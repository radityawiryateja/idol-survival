from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bot import start_bot, stop_bot
from app.config import settings
from app.routers import auth, protected, idols, leaderboard, tasks, dashboard, rewards, shop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run the Telegram bot's long-polling loop as a background task so it
    # doesn't block Uvicorn's event loop.
    await start_bot()
    yield
    await stop_bot()


app = FastAPI(title="Idol Survival API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(protected.router, prefix="/api", tags=["protected"])
app.include_router(idols.router, prefix="/api", tags=["idols"])
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(rewards.router, prefix="/api", tags=["rewards"])
app.include_router(shop.router, prefix="/api", tags=["shop"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "idol-survival-api"}
