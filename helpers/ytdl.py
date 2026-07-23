"""
Free "no paid API" music source.

There is no genuinely free official music-file API, so the standard
workaround ("jugad") every open-source Telegram music bot uses is to
pull audio straight from YouTube with yt-dlp — no key, no quota, no
cost. This module wraps that.

NOTE: Downloading copyrighted audio may violate YouTube's Terms of
Service depending on how you use it. Use responsibly / for
personal, fair-use, or licensed content.
"""

import asyncio
import os
import yt_dlp
from config import DOWNLOADS_DIR

YDL_SEARCH_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "skip_download": True,
}

YDL_DOWNLOAD_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "outtmpl": os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s"),
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


def _search(query: str) -> dict | None:
    with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        entries = info.get("entries") or []
        return entries[0] if entries else None


async def search_track(query: str) -> dict | None:
    """Search YouTube for `query`, return metadata dict or None."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _search, query)


def _download(video_id_or_url: str) -> str:
    with yt_dlp.YoutubeDL(YDL_DOWNLOAD_OPTS) as ydl:
        info = ydl.extract_info(video_id_or_url, download=True)
        path = ydl.prepare_filename(info)
        # postprocessor changes extension to mp3
        base, _ = os.path.splitext(path)
        mp3_path = base + ".mp3"
        return mp3_path if os.path.exists(mp3_path) else path


async def download_track(video_id_or_url: str) -> str:
    """Download audio, return local file path (mp3)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download, video_id_or_url)


def fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return "Live/Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"
