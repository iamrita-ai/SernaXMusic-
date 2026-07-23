"""
Voice-Chat streaming layer.

A Telegram *bot* account can never join a group Voice Chat — that's a
Bot API limitation, not a bug. The workaround every VC-music-bot uses
is a second, normal user account ("assistant") logged in via Pyrogram
(MTProto), which PyTgCalls then uses to actually join & stream audio
into the call.

This module is a no-op / disabled shim if API_ID / API_HASH /
STRING_SESSION are not supplied — the rest of the bot (search +
send-as-audio-file) keeps working regardless.
"""

import logging
from config import API_ID, API_HASH, STRING_SESSION, VC_ENABLED

log = logging.getLogger("serenaxmusic.vc")

pyro_client = None
call_py = None

if VC_ENABLED:
    from pyrogram import Client
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream

    pyro_client = Client(
        name="serenax_assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        in_memory=True,
    )
    call_py = PyTgCalls(pyro_client)


async def start_vc_client():
    if not VC_ENABLED:
        log.warning(
            "VC streaming disabled — set API_ID, API_HASH and STRING_SESSION "
            "to enable group Voice Chat streaming."
        )
        return
    await pyro_client.start()
    await call_py.start()
    log.info("Assistant + PyTgCalls started — VC streaming is live.")


async def join_and_stream(chat_id: int, file_path: str):
    """Join (if needed) the group's VC and stream `file_path`."""
    if not VC_ENABLED:
        raise RuntimeError(
            "Voice-Chat streaming is not configured on this deployment "
            "(missing API_ID / API_HASH / STRING_SESSION)."
        )
    from pytgcalls.types import MediaStream

    try:
        await call_py.play(chat_id, MediaStream(file_path))
    except Exception:
        # not yet in the call -> join it with this stream
        await call_py.play(chat_id, MediaStream(file_path))


async def change_stream(chat_id: int, file_path: str):
    from pytgcalls.types import MediaStream

    await call_py.play(chat_id, MediaStream(file_path))


async def leave_vc(chat_id: int):
    if VC_ENABLED:
        await call_py.leave_call(chat_id)


async def pause_vc(chat_id: int):
    if VC_ENABLED:
        await call_py.pause_stream(chat_id)


async def resume_vc(chat_id: int):
    if VC_ENABLED:
        await call_py.resume_stream(chat_id)
