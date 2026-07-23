import logging
import os

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN, VC_ENABLED
from modules import start, play, controls, broadcast, admin, session_gen
from modules import vc as vc_module

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("serenaxmusic")


async def _post_init(app: Application):
    if VC_ENABLED:
        await vc_module.start_vc_client()
    log.info("SerenaXMusic is up and running ✅")


async def _on_error(update, context: ContextTypes.DEFAULT_TYPE):
    log.error("Unhandled exception while processing an update", exc_info=context.error)


def build_app() -> Application:
    if not BOT_TOKEN:
        raise SystemExit(
            "❌ BOT_TOKEN missing. Set it in your environment / .env before starting."
        )

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()

    # ---- start / help ----
    app.add_handler(CommandHandler("start", start.start_cmd))
    app.add_handler(CommandHandler("help", start.help_cmd))
    app.add_handler(CommandHandler("ping", start.ping_cmd))
    app.add_handler(CallbackQueryHandler(start.help_back_callback, pattern="^help_back$"))
    app.add_handler(CallbackQueryHandler(start.help_callback, pattern="^help_\\d+$"))

    # ---- playback ----
    app.add_handler(CommandHandler("play", play.play_cmd))
    app.add_handler(CommandHandler("vplay", play.play_cmd))
    app.add_handler(CommandHandler("playnext", play.playnext_cmd))

    # ---- controls ----
    app.add_handler(CommandHandler("skip", controls.skip_cmd))
    app.add_handler(CommandHandler("pause", controls.pause_cmd))
    app.add_handler(CommandHandler("resume", controls.resume_cmd))
    app.add_handler(CommandHandler("end", controls.end_cmd))
    app.add_handler(CommandHandler("stop", controls.end_cmd))
    app.add_handler(CommandHandler("shuffle", controls.shuffle_cmd))
    app.add_handler(CommandHandler("repeat", controls.repeat_cmd))
    app.add_handler(CommandHandler("queue", controls.queue_cmd))

    # ---- admin ----
    app.add_handler(CommandHandler("broadcast", broadcast.broadcast_cmd))
    app.add_handler(CommandHandler("stats", admin.stats_cmd))

    # ---- in-bot secure STRING_SESSION generator (owner, DM only) ----
    app.add_handler(session_gen.build_conversation_handler())

    app.add_error_handler(_on_error)

    return app


if __name__ == "__main__":
    application = build_app()

    port = int(os.environ.get("PORT", 10000))
    # Render sets this automatically for every Web Service.
    external_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("WEBHOOK_URL")

    if external_url:
        # Webhook mode — the correct way to run on a Render Web Service.
        # Only ONE instance ever holds the webhook registration with
        # Telegram, so the "Conflict: terminated by other getUpdates
        # request" error (caused by two polling instances overlapping
        # during a zero-downtime deploy) simply can't happen anymore.
        # This also binds $PORT itself, so no separate health server
        # is needed for Render's port scan.
        webhook_path = BOT_TOKEN
        log.info(f"Starting in WEBHOOK mode -> {external_url}/{webhook_path}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=f"{external_url.rstrip('/')}/{webhook_path}",
            drop_pending_updates=True,
        )
    else:
        # Local development / any host without a public URL -> polling.
        log.info("RENDER_EXTERNAL_URL not set -> starting in POLLING mode (local dev).")
        application.run_polling(drop_pending_updates=True)
