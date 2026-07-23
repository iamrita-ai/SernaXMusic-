"""Small reusable decorators for handlers."""

import functools
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_IDS


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *a, **kw):
        user = update.effective_user
        if not user or user.id not in OWNER_IDS:
            await update.effective_message.reply_text(
                "🚫 Ye command sirf bot owners ke liye hai."
            )
            return
        return await func(update, context, *a, **kw)

    return wrapper
