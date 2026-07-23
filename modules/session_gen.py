"""
Lets an OWNER generate a Pyrogram STRING_SESSION from inside the bot
itself (DM only), instead of running a separate local script.

Security measures:
- Only works in a private chat with an owner (checked twice).
- Phone/code/password prompts explicitly warn the user.
- The final string-session message is auto-deleted after 60s.
- The Pyrogram client used for login is temporary and disconnected
  right after, whether it succeeds or fails.
- Nothing is written to disk or the database at any point.
"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import OWNER_IDS, API_ID, API_HASH

log = logging.getLogger("serenaxmusic.session_gen")

PHONE, CODE, PASSWORD = range(3)


def _is_owner_dm(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    return bool(user and user.id in OWNER_IDS and chat and chat.type == chat.PRIVATE)


async def genstring_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_owner_dm(update):
        if update.effective_chat.type != update.effective_chat.PRIVATE:
            await update.effective_message.reply_text(
                "🔒 Security ke liye ye command sirf bot ki DM me chalta hai."
            )
        else:
            await update.effective_message.reply_text("🚫 Ye command sirf bot owners ke liye hai.")
        return ConversationHandler.END

    if not (API_ID and API_HASH):
        await update.effective_message.reply_text(
            "⚠️ Pehle API_ID aur API_HASH environment variables set karo, "
            "phir /genstring try karo."
        )
        return ConversationHandler.END

    from pyrogram import Client

    client = Client("session_gen_temp", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await client.connect()
    context.user_data["pg_client"] = client

    await update.effective_message.reply_text(
        "📱 Apna phone number *country code ke saath* bhejo (jaise `+919876543210`).\n\n"
        "⚠️ Ye account jo bhi phone number doge, wahi Group Voice Chat streaming ke "
        "liye assistant ban jayega. Recommend: apna primary personal number *mat* use "
        "karo — ek alag/secondary number behtar hai.\n\n"
        "Cancel karne ke liye /cancel bhejo.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return PHONE


async def genstring_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.effective_message.text.strip()
    client = context.user_data.get("pg_client")

    try:
        sent = await client.send_code(phone)
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Code bhejne me error: {e}")
        await client.disconnect()
        return ConversationHandler.END

    context.user_data["phone"] = phone
    context.user_data["phone_code_hash"] = sent.phone_code_hash

    await update.effective_message.reply_text(
        "🔑 Telegram ne aapko ek login code bheja hai.\n\n"
        "Us code ke digits ke *beech me space* daal kar yaha bhejo — jaise agar code "
        "`12345` hai to `1 2 3 4 5` bhejo. (Ye Telegram ke auto-detect/interception "
        "se bachane ka tarika hai.)",
        parse_mode=ParseMode.MARKDOWN,
    )
    return CODE


async def genstring_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired

    code = update.effective_message.text.strip().replace(" ", "")
    client = context.user_data.get("pg_client")
    phone = context.user_data.get("phone")
    phone_code_hash = context.user_data.get("phone_code_hash")

    try:
        await client.sign_in(phone, phone_code_hash, code)
    except SessionPasswordNeeded:
        await update.effective_message.reply_text(
            "🔐 Is account par 2-Step Verification (cloud password) on hai. "
            "Apna password bhejo:"
        )
        return PASSWORD
    except (PhoneCodeInvalid, PhoneCodeExpired) as e:
        await update.effective_message.reply_text(f"❌ Code galat/expire ho gaya: {e}\n/genstring se dobara try karo.")
        await client.disconnect()
        return ConversationHandler.END
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error: {e}")
        await client.disconnect()
        return ConversationHandler.END

    return await _finish(update, context)


async def genstring_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from pyrogram.errors import PasswordHashInvalid

    password = update.effective_message.text.strip()
    client = context.user_data.get("pg_client")

    try:
        await client.check_password(password)
    except PasswordHashInvalid:
        await update.effective_message.reply_text("❌ Password galat hai. Dobara bhejo, ya /cancel karo.")
        return PASSWORD
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error: {e}")
        await client.disconnect()
        return ConversationHandler.END

    return await _finish(update, context)


async def _finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = context.user_data.get("pg_client")
    session_string = await client.export_session_string()
    await client.disconnect()
    context.user_data.clear()

    warn = await update.effective_message.reply_text(
        "✅ *STRING_SESSION generate ho gaya.*\n\n"
        "Ye neeche wala message **60 seconds** me apne aap delete ho jayega — "
        "isse turant copy karke apni Render env variable `STRING_SESSION` me paste "
        "kar do, aur is chat ko bhi manually clear kar dena.\n\n"
        "⚠️ Ye string tumhare Telegram account ki full login key hai — kisi ke "
        "saath share mat karo.",
        parse_mode=ParseMode.MARKDOWN,
    )
    session_msg = await update.effective_message.reply_text(f"`{session_string}`", parse_mode=ParseMode.MARKDOWN)

    context.job_queue.run_once(
        _delete_message_job,
        60,
        data={"chat_id": session_msg.chat_id, "message_id": session_msg.message_id},
    )
    return ConversationHandler.END


async def _delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    try:
        await context.bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    except Exception:
        pass


async def genstring_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = context.user_data.get("pg_client")
    if client:
        try:
            await client.disconnect()
        except Exception:
            pass
    context.user_data.clear()
    await update.effective_message.reply_text("❎ Cancel kar diya.")
    return ConversationHandler.END


def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("genstring", genstring_start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, genstring_phone)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, genstring_code)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, genstring_password)],
        },
        fallbacks=[CommandHandler("cancel", genstring_cancel)],
        conversation_timeout=300,
    )
