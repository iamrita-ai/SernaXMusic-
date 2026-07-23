from telegram import Update, Chat
from telegram.constants import ParseMode, ChatAction
from telegram.ext import ContextTypes

from config import ETA_GIF, ETA_STICKER, VC_ENABLED
from helpers.ytdl import search_track, download_track, fmt_duration
from helpers.queue import Track, add_track, get_state, play_next_now
from modules import vc


async def _send_eta(update: Update):
    """Show an ETA gif/sticker while we search + download — feels alive."""
    msg = update.effective_message
    if ETA_GIF:
        return await msg.reply_animation(animation=ETA_GIF, caption="🔎 Dhoond raha hu...")
    if ETA_STICKER:
        return await msg.reply_sticker(sticker=ETA_STICKER)
    return await msg.reply_text("🔎 Dhoond raha hu...")


async def _resolve_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    msg = update.effective_message
    if context.args:
        return " ".join(context.args)
    if msg.reply_to_message and msg.reply_to_message.audio:
        return msg.reply_to_message.audio.title or msg.reply_to_message.audio.file_name
    return None


async def play_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = await _resolve_query(update, context)
    if not query:
        await update.effective_message.reply_text(
            "❓ Gaane ka naam do — jaise:\n<code>/play tum hi ho</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    chat = update.effective_chat
    eta_msg = await _send_eta(update)
    await context.bot.send_chat_action(chat.id, ChatAction.RECORD_VOICE)

    info = await search_track(query)
    if not info:
        await eta_msg.edit_text("❌ Kuch nahi mila, doosra naam try karo.")
        return

    title = info.get("title", "Unknown")
    duration = fmt_duration(info.get("duration"))
    url = info.get("webpage_url") or info.get("url")

    file_path = await download_track(url)
    track = Track(
        title=title,
        duration=duration,
        webpage_url=url,
        file_path=file_path,
        requested_by=update.effective_user.id,
    )

    caption = (
        f"🎶 <b>{title}</b>\n"
        f"⏱ Duration: <code>{duration}</code>\n"
        f"🙋 Requested by: {update.effective_user.mention_html()}"
    )

    if chat.type == Chat.PRIVATE or not VC_ENABLED:
        # DM (or VC not configured on this deployment) -> send as an audio file
        await eta_msg.delete()
        await context.bot.send_audio(
            chat_id=chat.id,
            audio=open(file_path, "rb"),
            title=title,
            caption=caption,
            parse_mode=ParseMode.HTML,
        )
        return

    # Group chat + VC configured -> stream into the Voice Chat
    state = get_state(chat.id)
    if state.is_playing:
        add_track(chat.id, track)
        await eta_msg.edit_text(
            f"➕ Queue me add ho gaya: <b>{title}</b> (position {len(state.queue)})",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await vc.join_and_stream(chat.id, file_path)
        state.is_playing = True
        await eta_msg.edit_text(
            f"▶️ <b>Ab baj raha hai (Group Voice Chat):</b>\n{caption}",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await eta_msg.edit_text(f"⚠️ VC stream fail ho gaya: {e}\nAudio file bhej raha hu instead.")
        await context.bot.send_audio(chat.id, audio=open(file_path, "rb"), title=title)


async def playnext_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = await _resolve_query(update, context)
    if not query:
        await update.effective_message.reply_text("❓ Gaane ka naam do: <code>/playnext naam</code>", parse_mode=ParseMode.HTML)
        return

    msg = await update.effective_message.reply_text("🔎 Dhoond raha hu...")
    info = await search_track(query)
    if not info:
        await msg.edit_text("❌ Kuch nahi mila.")
        return

    url = info.get("webpage_url") or info.get("url")
    file_path = await download_track(url)
    track = Track(
        title=info.get("title", "Unknown"),
        duration=fmt_duration(info.get("duration")),
        webpage_url=url,
        file_path=file_path,
        requested_by=update.effective_user.id,
    )
    play_next_now(update.effective_chat.id, track)
    await msg.edit_text(f"⏭ Agli baari play hoga: <b>{track.title}</b>", parse_mode=ParseMode.HTML)
