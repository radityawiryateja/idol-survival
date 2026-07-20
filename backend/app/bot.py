import asyncio
import logging
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.services import supabase_client

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


async def _upload_photo_to_storage(file_id: str) -> str:
    file = await bot.get_file(file_id)
    file_bytes_io = await bot.download_file(file.file_path)
    file_bytes = file_bytes_io.read()

    path = f"broadcasts/{uuid.uuid4()}.jpg"
    await supabase_client.supabase.storage.from_("idol-media").upload(
        path, file_bytes, {"content-type": "image/jpeg"}
    )
    
    public_url = await supabase_client.supabase.storage.from_("idol-media").get_public_url(path)
    
    return public_url


@dp.message(F.chat.type.in_({"private", "group", "supergroup"}))
async def handle_idol_broadcast(message: Message):
    idol = await _find_idol_by_admin_chat(message.chat.id)
    if not idol:
        return

    if message.photo:
        photo = message.photo[-1]
        try:
            media_url = await _upload_photo_to_storage(photo.file_id)
        except Exception as exc:
            logger.error(f"Failed to upload broadcast photo: {exc}")
            return

        await supabase_client.supabase.table("idol_broadcasts").insert(
            {
                "idol_id": idol["id"],
                "content": message.caption,
                "media_url": media_url,
                "media_type": "photo",
            }
        ).execute()
        return

    if message.text:
        await supabase_client.supabase.table("idol_broadcasts").insert(
            {"idol_id": idol["id"], "content": message.text, "media_type": "text"}
        ).execute()
        

async def forward_reply_to_idol(idol_admin_chat_id: int, text: str) -> int | None:
    """Dipanggil dari FastAPI saat user kirim reply, forward ke chat admin idol."""
    sent = await bot.send_message(chat_id=idol_admin_chat_id, text=text)
    return sent.message_id
