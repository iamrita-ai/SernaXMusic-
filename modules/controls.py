from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import VC_ENABLED
from helpers.queue import (
    get_state, pop_next, shuffle_queue, clear_queue, toggle_repeat,
)
from modules import vc


def _require_vc(update: Update) -> bool:
    return update.effective_chat.type != "private"


async def skip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    nxt = pop_next(chat_id)
    if not nxt:
        get_state(chat_id).is_playing = False
        if VC_ENABLED:
            await vc.leave_vc(chat_id)
        await update.effective_message.reply_text("⏹ Queue khaali hai, ruk gaya.")
        return

    if VC_ENABLED:
        await vc.change_stream(chat_id, nxt.file_path)
    await update.effective_message.reply_text(
        f"⏭ Skip! Ab baj raha hai: <b>{nxt.title}</b>", parse_mode=ParseMode.HTML
    )


async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not VC_ENABLED:
        await update.effective_message.reply_text("⚠️ VC streaming enabled nahi hai is deployment par.")
        return
    await vc.pause_vc(update.effective_chat.id)
    await update.effective_message.reply_text("⏸ Paused.")


async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not VC_ENABLED:
        await update.effective_message.reply_text("⚠️ VC streaming enabled nahi hai is deployment par.")
        return
    await vc.resume_vc(update.effective_chat.id)
    await update.effective_message.reply_text("▶️ Resumed.")


async def end_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clear_queue(chat_id)
    get_state(chat_id).is_playing = False
    if VC_ENABLED:
        await vc.leave_vc(chat_id)
    await update.effective_message.reply_text("🛑 Stream band, queue clear ho gayi.")


async def shuffle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    shuffle_queue(chat_id)
    await update.effective_message.reply_text("🔀 Queue shuffle ho gayi.")


async def repeat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = toggle_repeat(chat_id)
    await update.effective_message.reply_text(
        f"🔁 Repeat mode: <b>{'ON' if state else 'OFF'}</b>", parse_mode=ParseMode.HTML
    )


async def queue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_chat.id)
    if not state.queue:
        await update.effective_message.reply_text("📭 Queue khaali hai.")
        return
    lines = [f"{i+1}. {t.title} — {t.duration}" for i, t in enumerate(state.queue)]
    await update.effective_message.reply_text(
        "📜 <b>Current Queue:</b>\n<pre>" + "\n".join(lines) + "</pre>",
        parse_mode=ParseMode.HTML,
    )
