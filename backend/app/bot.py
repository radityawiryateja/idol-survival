"""
aiogram bot that runs concurrently with the FastAPI server via asyncio
background tasks (see main.py's lifespan handler). It doesn't block or
share a thread with the HTTP server.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Selamat datang di Idol Survival Producer Bot!\n"
        "Buka web app dan tekan tombol Login with Telegram untuk masuk "
        "ke dashboard producer-mu."
    )


_polling_task: asyncio.Task | None = None


async def start_bot() -> asyncio.Task:
    global _polling_task
    logger.info("Starting Telegram bot polling...")
    _polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    return _polling_task


async def stop_bot() -> None:
    global _polling_task
    logger.info("Stopping Telegram bot...")
    if _polling_task and not _polling_task.done():
        _polling_task.cancel()
    await bot.session.close()
