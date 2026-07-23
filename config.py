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
# YouTube cookies — cloud hosts (Render, etc.) get IP-blocked by YouTube
# with "Sign in to confirm you're not a bot." Paste a Netscape-format
# cookies.txt content here (export via a browser extension like
# "Get cookies.txt LOCALLY" while logged into YouTube) to fix it.
# Optional — bot works without it until YouTube starts blocking you.
# ---------------------------------------------------------------------
YT_COOKIES = os.environ.get("YT_COOKIES", "").strip()

# ---------------------------------------------------------------------
# Proxy — YouTube blocklists most datacenter IPs (Render/Railway/Heroku
# included), so a proxy is often required for search/download to work.
#
#   PROXY_URL   -> single proxy, e.g. http://user:pass@host:port
#   PROXY_LIST  -> comma-separated list of proxies to rotate through,
#                  one is picked round-robin on every search/download.
#                  PROXY_LIST overrides PROXY_URL if both are set.
# ---------------------------------------------------------------------
PROXY_URL = os.environ.get("PROXY_URL", "").strip()
PROXY_LIST = [p.strip() for p in os.environ.get("PROXY_LIST", "").split(",") if p.strip()]

# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------
_raw_support_chat = os.environ.get("SUPPORT_CHAT", "").strip()
if not _raw_support_chat:
    SUPPORT_CHAT = None  # button simply won't be shown
elif _raw_support_chat.startswith("http://") or _raw_support_chat.startswith("https://"):
    SUPPORT_CHAT = _raw_support_chat
else:
    # handles bare usernames ("mychat"), "@mychat", or invite hashes ("+abc123")
    SUPPORT_CHAT = "https://t.me/" + _raw_support_chat.lstrip("@")
DURATION_LIMIT_MIN = _int_env("DURATION_LIMIT_MIN", 60)
DOWNLOADS_DIR = "downloads"

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
