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
import itertools
import os
import yt_dlp
from config import DOWNLOADS_DIR, YT_COOKIES, PROXY_URL, PROXY_LIST

COOKIES_PATH = os.path.join(DOWNLOADS_DIR, "cookies.txt")

if YT_COOKIES:
    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        f.write(YT_COOKIES + "\n")

_proxy_cycle = itertools.cycle(PROXY_LIST) if PROXY_LIST else None


def _next_proxy() -> str | None:
    """Round-robin through PROXY_LIST if set, else fall back to PROXY_URL."""
    if _proxy_cycle:
        return next(_proxy_cycle)
    return PROXY_URL or None


def _base_opts() -> dict:
    opts = {
        # "android" client usually isn't hit with the "Sign in to confirm
        # you're not a bot" wall that cloud-host IPs get on the web client.
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {"User-Agent": "com.google.android.youtube/19.29.37"},
    }
    if YT_COOKIES:
        opts["cookiefile"] = COOKIES_PATH
    proxy = _next_proxy()
    if proxy:
        opts["proxy"] = proxy
    return opts


def _search(query: str) -> dict | None:
    attempts = min(len(PROXY_LIST), 3) or 1
    for _ in range(attempts):
        opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "default_search": "ytsearch",
            "skip_download": True,
            **_base_opts(),
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                entries = info.get("entries") or []
                return entries[0] if entries else None
        except yt_dlp.utils.DownloadError:
            continue  # try the next proxy in rotation, if any
    return None


async def search_track(query: str) -> dict | None:
    """Search YouTube for `query`, return metadata dict or None."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _search, query)


def _download(video_id_or_url: str) -> str:
    attempts = min(len(PROXY_LIST), 3) or 1
    last_err = None
    for _ in range(attempts):
        opts = {
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
            **_base_opts(),
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_id_or_url, download=True)
                path = ydl.prepare_filename(info)
                base, _ext = os.path.splitext(path)
                mp3_path = base + ".mp3"
                return mp3_path if os.path.exists(mp3_path) else path
        except yt_dlp.utils.DownloadError as e:
            last_err = e
            continue
    raise last_err


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
