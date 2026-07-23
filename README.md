# 🎵 SernaXMusic (@SerenaXmusicBot)

A Telegram music bot built on **python-telegram-bot v22.8**, capable of:

- 🔎 Searching + sending songs as **audio files** (DM or group)
- 🎙 **Streaming into Group Voice Chats** (via a Pyrogram assistant + PyTgCalls)
- 🔀 Queue system — `/shuffle`, `/repeat`, `/playnext`, `/skip`, `/pause`, `/resume`, `/queue`, `/end`
- 📢 `/broadcast` — reply to **any** message type (text/photo/video/sticker/etc.) to broadcast it to every served user & chat
- 🗄 Optional MongoDB persistence for the broadcast list
- 🎬 Configurable Start/ETA GIFs & stickers (Giphy links)
- 👑 Two hard-coded owners

> No paid music API is used. Audio comes from YouTube via `yt-dlp` — the
> standard free workaround ("jugad") every open-source Telegram music
> bot relies on. Use responsibly / for personal & fair-use purposes.

---

## 📁 Project Structure

```
SerenaXMusic/
├── config.py              # all env-driven configuration
├── main.py                # entry point, registers handlers
├── database/
│   └── mongo.py           # optional MongoDB layer (graceful fallback)
├── helpers/
│   ├── decorators.py      # @owner_only
│   ├── queue.py           # in-memory per-chat queue
│   ├── ytdl.py            # yt-dlp search/download (the "free API")
│   └── generate_session.py# one-time Pyrogram STRING_SESSION generator
├── modules/
│   ├── start.py           # /start /help /ping
│   ├── play.py             # /play /vplay /playnext
│   ├── controls.py        # /skip /pause /resume /end /shuffle /repeat /queue
│   ├── broadcast.py        # /broadcast
│   ├── admin.py            # /stats
│   └── vc.py               # Pyrogram + PyTgCalls streaming layer
├── requirements.txt
├── Procfile                 # Render worker start command
├── runtime.txt
├── .env.example
└── .gitignore
```

---

## ⚙️ Environment Variables

Copy `.env.example` → `.env` (locally) or paste into Render's **Environment** tab.

| Variable | Required? | Purpose |
|---|---|---|
| `BOT_TOKEN` | ✅ Yes | From [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` / `BOT_NAME` | optional | Cosmetic, used in buttons |
| `API_ID` / `API_HASH` | Only for VC streaming | From https://my.telegram.org |
| `STRING_SESSION` | Only for VC streaming | Generate with `python helpers/generate_session.py` |
| `MONGO_URI` | optional | Enables persistent broadcast lists |
| `LOG_GROUP_ID` | optional | Bot logs group |
| `START_GIF` / `ETA_GIF` / `START_STICKER` / `ETA_STICKER` | optional | Giphy/Telegram links |
| `SUPPORT_CHAT` | optional | Support chat link shown on `/start` |
| `DURATION_LIMIT_MIN` | optional | Max track length allowed |

Owners are **hard-coded** in `config.py`:
```python
OWNER_IDS = {6518065496, 1598576202}
```

⚠️ **Important:** If `API_ID`/`API_HASH`/`STRING_SESSION` are left empty,
Voice-Chat streaming auto-disables and the bot simply sends songs as
audio files instead — nothing crashes.

---

## 🚀 Deploying on Render

1. Push this repo to GitHub.
2. Render → New → **Background Worker** → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python3 main.py` (already in `Procfile`)
5. Add the environment variables above under **Environment**.
6. Deploy 🎉

You'll also need **FFmpeg** available in the build environment (Render's
default Python image ships without it) — add a file named
`Aptfile`/`nixpacks.toml`, or use a Docker-based Render service that
installs `ffmpeg`, e.g.:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "main.py"]
```

---

## 🖥 Running Locally

```bash
git clone <your-repo-url>
cd SerenaXMusic
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in BOT_TOKEN at minimum
python3 main.py
```

To enable Voice-Chat streaming, first generate a session string:
```bash
python helpers/generate_session.py
```
then paste it into `STRING_SESSION` in `.env`.

---

## 📜 Commands

**Playback:** `/play`, `/vplay`, `/playnext`, `/skip`, `/pause`, `/resume`, `/end`
**Queue:** `/queue`, `/shuffle`, `/repeat`
**Info:** `/start`, `/help`, `/ping`, `/stats`
**Owner:** `/broadcast` (reply to any message)

---

## ⚠️ Notes & Limits

- This is a **scaffold/professional starter**, wired end-to-end and
  runnable — test thoroughly in a private group before public use.
- Downloading copyrighted tracks from YouTube may breach its Terms of
  Service depending on your jurisdiction/use-case; you are responsible
  for how you operate the bot.
- `py-tgcalls` requires `ffmpeg` on the host machine.
