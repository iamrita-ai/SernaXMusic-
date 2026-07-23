from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import BOT_NAME, BOT_USERNAME, START_GIF, START_STICKER, SUPPORT_CHAT
from database.mongo import add_served_user, add_served_chat

HELP_CATEGORIES = {
    "🎵 Playback": (
        "/play <name|reply audio> — search & play/stream a track\n"
        "/vplay <name> — play as a video call stream\n"
        "/playnext <name> — queue a track to play right after current\n"
        "/skip — skip current track\n"
        "/pause — pause playback\n"
        "/resume — resume playback\n"
        "/end — stop & clear the queue"
    ),
    "🔀 Queue Controls": (
        "/queue — show current queue\n"
        "/shuffle — shuffle the queue\n"
        "/repeat — toggle repeat mode for current track"
    ),
    "🛠 Admin / Owner": (
        "/broadcast (reply to any message) — broadcast it to all users\n"
        "/stats — bot stats\n"
        "/ping — check latency"
    ),
}


async def _register(update: Update):
    chat = update.effective_chat
    user = update.effective_user
    if user:
        await add_served_user(user.id)
    if chat and chat.type != chat.PRIVATE:
        await add_served_chat(chat.id)


def _help_keyboard() -> InlineKeyboardMarkup:
    # `style` needs PTB >= 22.7 and a Telegram client released after Feb 9,
    # 2026 to actually render in color — older clients just show a plain
    # button, so nothing breaks either way.
    rows = [[InlineKeyboardButton(cat, callback_data=f"help_{i}", style="primary")]
            for i, cat in enumerate(HELP_CATEGORIES)]
    rows.append([InlineKeyboardButton(
        "➕ Add me to your group",
        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        style="success",
    )])
    rows.append([InlineKeyboardButton("🆘 Support Chat", url=SUPPORT_CHAT, style="primary")])
    return InlineKeyboardMarkup(rows)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _register(update)
    user = update.effective_user
    text = (
        f"👋 <b>Namaste {user.mention_html()}!</b>\n\n"
        f"Main <b>{BOT_NAME}</b> hu — fast music + Group Voice Chat streaming bot.\n\n"
        "🎧 Koi bhi gaana bhejo (<code>/play song name</code>) — mai use dhoond kar "
        "audio file ya group VC me live stream kar dunga.\n\n"
        "Neeche category-wise commands dekho 👇"
    )
    kb = _help_keyboard()

    if START_GIF:
        await update.effective_message.reply_animation(
            animation=START_GIF, caption=text, parse_mode=ParseMode.HTML, reply_markup=kb
        )
    elif START_STICKER:
        await update.effective_message.reply_sticker(sticker=START_STICKER)
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "📚 <b>Help Menu</b> — category chuno:",
        parse_mode=ParseMode.HTML,
        reply_markup=_help_keyboard(),
    )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_", 1)[1])
    cat_name = list(HELP_CATEGORIES)[idx]
    body = HELP_CATEGORIES[cat_name]
    text = f"<b>{cat_name}</b>\n\n<pre>{body}</pre>"
    back_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("« Back", callback_data="help_back", style="danger")]]
    )
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_kb)


async def help_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📚 <b>Help Menu</b> — category chuno:",
        parse_mode=ParseMode.HTML,
        reply_markup=_help_keyboard(),
    )


async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🏓 Pong! Bot alive hai.")
