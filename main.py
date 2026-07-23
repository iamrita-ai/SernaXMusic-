import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from config import BOT_TOKEN, VC_ENABLED
from modules import start, play, controls, broadcast, admin
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

    return app


if __name__ == "__main__":
    application = build_app()
    application.run_polling(drop_pending_updates=True)
