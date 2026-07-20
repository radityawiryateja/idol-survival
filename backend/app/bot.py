import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.services import supabase_client

# aiogram's default logging is very chatty (it logs every single polling
# update at INFO level). We keep third-party loggers at WARNING and only
# raise our own logger to INFO for the handful of lifecycle events we
# actually care about, so the console stays readable in production.
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("idol_survival.bot")
logger.setLevel(logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Maps a Telegram message media kind to the media_type value stored in
# idol_broadcasts / used by the frontend to pick the right player.
_MEDIA_TYPES = {
    "photo": "photo",
    "video": "video",
    "video_note": "video_note",  # round "live motion" video message
    "voice": "voice",
    "audio": "audio",
}


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


async def _find_idol_by_admin_chat(chat_id: int):
    result = await supabase_client.supabase.table("idols").select("*").eq("telegram_admin_chat_id", chat_id).execute()
    return result.data[0] if result.data else None


@dp.message(F.reply_to_message, F.chat.type.in_({"private", "group", "supergroup"}))
async def handle_idol_private_reply(message: Message):
    """
    Kalau admin idol me-reply pesan yang di-forward dari user, itu berarti
    balasan privat — bukan broadcast ke semua orang.
    """
    idol = await _find_idol_by_admin_chat(message.chat.id)
    if not idol:
        return

    original = (
        await supabase_client.supabase.table("idol_private_messages")
        .select("producer_id")
        .eq("telegram_message_id", message.reply_to_message.message_id)
        .eq("sender", "user")
        .execute()
    ).data
    if not original:
        return  # reply ke pesan yang bukan forward-an user, abaikan

    await supabase_client.supabase.table("idol_private_messages").insert(
        {
            "idol_id": idol["id"],
            "producer_id": original[0]["producer_id"],
            "sender": "idol",
            "content": message.text or message.caption,
            "media_type": "text",
        }
    ).execute()


async def _upload_to_storage(file_id: str, folder: str, extension: str, content_type: str) -> str:
    file = await bot.get_file(file_id)
    file_bytes_io = await bot.download_file(file.file_path)
    file_bytes = file_bytes_io.read()

    path = f"{folder}/{uuid.uuid4()}.{extension}"
    await supabase_client.supabase.storage.from_("idol-media").upload(
        path, file_bytes, {"content-type": content_type}
    )
    return await supabase_client.supabase.storage.from_("idol-media").get_public_url(path)


async def _insert_broadcast(idol_id: str, content: str | None, media_url: str | None, media_type: str) -> None:
    await supabase_client.supabase.table("idol_broadcasts").insert(
        {
            "idol_id": idol_id,
            "content": content,
            "media_url": media_url,
            "media_type": media_type,
        }
    ).execute()


@dp.message(F.chat.type.in_({"private", "group", "supergroup"}))
async def handle_idol_broadcast(message: Message):
    idol = await _find_idol_by_admin_chat(message.chat.id)
    if not idol:
        return

    try:
        if message.photo:
            photo = message.photo[-1]
            media_url = await _upload_to_storage(photo.file_id, "broadcasts", "jpg", "image/jpeg")
            await _insert_broadcast(idol["id"], message.caption, media_url, _MEDIA_TYPES["photo"])
            return

        if message.video:
            media_url = await _upload_to_storage(message.video.file_id, "broadcasts", "mp4", "video/mp4")
            await _insert_broadcast(idol["id"], message.caption, media_url, _MEDIA_TYPES["video"])
            return

        if message.video_note:
            # Telegram's round self-recorded video — the closest match to a
            # "Live Photo" / motion photo. No caption support on these.
            media_url = await _upload_to_storage(message.video_note.file_id, "broadcasts", "mp4", "video/mp4")
            await _insert_broadcast(idol["id"], None, media_url, _MEDIA_TYPES["video_note"])
            return

        if message.voice:
            media_url = await _upload_to_storage(message.voice.file_id, "broadcasts", "ogg", "audio/ogg")
            await _insert_broadcast(idol["id"], message.caption, media_url, _MEDIA_TYPES["voice"])
            return

        if message.audio:
            media_url = await _upload_to_storage(message.audio.file_id, "broadcasts", "mp3", "audio/mpeg")
            title = message.caption or message.audio.title
            await _insert_broadcast(idol["id"], title, media_url, _MEDIA_TYPES["audio"])
            return

        if message.text:
            await _insert_broadcast(idol["id"], message.text, None, "text")
    except Exception:
        # A failed upload shouldn't crash the bot's polling loop — log once,
        # at warning level, and move on.
        logger.warning("Failed to process broadcast media for idol %s", idol["id"], exc_info=True)


async def forward_reply_to_idol(idol_admin_chat_id: int, text: str) -> int | None:
    """Dipanggil dari FastAPI saat user kirim reply, forward ke chat admin idol."""
    sent = await bot.send_message(chat_id=idol_admin_chat_id, text=text)
    return sent.message_id
