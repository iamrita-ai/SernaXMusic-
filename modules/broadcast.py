import asyncio
from telegram import Update
from telegram.error import Forbidden, BadRequest
from telegram.ext import ContextTypes

from helpers.decorators import owner_only
from database.mongo import get_served_users, get_served_chats


@owner_only
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    target = msg.reply_to_message

    if not target:
        await msg.reply_text(
            "❗ Kisi bhi message (text/photo/video/sticker/audio...) ko "
            "*reply* karke /broadcast bhejo.",
            parse_mode="Markdown",
        )
        return

    users = await get_served_users()
    chats = await get_served_chats()
    destinations = set(users) | set(chats)

    status = await msg.reply_text(f"📢 Broadcasting to {len(destinations)} chats...")

    sent, failed = 0, 0
    for dest_id in destinations:
        try:
            # copy_message works for ANY message type: text, photo, video,
            # sticker, document, voice, animation, etc. — no need to branch.
            await context.bot.copy_message(
                chat_id=dest_id,
                from_chat_id=target.chat_id,
                message_id=target.message_id,
            )
            sent += 1
        except (Forbidden, BadRequest):
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # gentle rate-limit

    await status.edit_text(
        f"✅ Broadcast complete.\nSent: {sent}\nFailed: {failed}"
    )
