"""
SerenaXMusic — central configuration.

Everything is read from the environment (Render → Environment tab, or a
local .env file). Only BOT_TOKEN is truly required to boot the bot in
"file/search" mode. Voice-Chat streaming additionally needs API_ID,
API_HASH and STRING_SESSION. Everything else is optional and the bot
simply disables the related feature if it's missing.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default=None):
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


# ---------------------------------------------------------------------
# Owners — hard-coded as requested. These IDs always have full owner
# rights (broadcast, restart, sudo-add, etc.) regardless of what's in
# the database.
# ---------------------------------------------------------------------
OWNER_IDS = {6518065496, 1598576202}

# ---------------------------------------------------------------------
# Core bot identity
# ---------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_NAME = os.environ.get("BOT_NAME", "SernaXMusic")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "SerenaXmusicBot").lstrip("@")

# ---------------------------------------------------------------------
# Pyrogram assistant (required only for group VC streaming)
# ---------------------------------------------------------------------
API_ID = _int_env("API_ID")
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
VC_ENABLED = bool(API_ID and API_HASH and STRING_SESSION)

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_ENABLED = bool(MONGO_URI)

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
LOG_GROUP_ID = _int_env("LOG_GROUP_ID")

# ---------------------------------------------------------------------
# Media — GIFs / stickers for start & "searching" (ETA) messages.
# Paste Giphy/telegram-friendly links here (as env vars). If left
# blank the bot just sends plain text instead, so nothing breaks.
# ---------------------------------------------------------------------
START_GIF = os.environ.get("START_GIF", "")
ETA_GIF = os.environ.get("ETA_GIF", "")
START_STICKER = os.environ.get("START_STICKER", "")
ETA_STICKER = os.environ.get("ETA_STICKER", "")

# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/")
DURATION_LIMIT_MIN = _int_env("DURATION_LIMIT_MIN", 60)
DOWNLOADS_DIR = "downloads"

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
