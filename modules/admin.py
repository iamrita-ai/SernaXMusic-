import platform
import psutil
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import VC_ENABLED, DB_ENABLED
from database.mongo import get_served_users, get_served_chats


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_served_users()
    chats = await get_served_chats()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    text = (
        "📊 <b>SerenaXMusic Stats</b>\n\n"
        f"👤 Users: <code>{len(users)}</code>\n"
        f"👥 Chats: <code>{len(chats)}</code>\n"
        f"🎙 VC Streaming: <code>{'ON' if VC_ENABLED else 'OFF'}</code>\n"
        f"🗄 Database: <code>{'Connected' if DB_ENABLED else 'In-memory only'}</code>\n"
        f"🖥 CPU: <code>{cpu}%</code>  |  RAM: <code>{ram}%</code>\n"
        f"🐍 Python: <code>{platform.python_version()}</code>"
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
