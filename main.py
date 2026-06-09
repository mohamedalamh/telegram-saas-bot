import os

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

import bot
import database as db

TOKEN = os.getenv("BOT_TOKEN")

print("================================")
print("TOKEN =", repr(TOKEN))
print("================================")


def main():

    if not TOKEN:
        raise Exception(
            "BOT_TOKEN variable not found in Railway Variables"
        )

    db.init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            bot.start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            bot.button
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            bot.text_handler
        )
    )

    print("🚀 SaaS RUNNING")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
