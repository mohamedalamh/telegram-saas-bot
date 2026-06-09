import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import bot
import database

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


def main():
    database.init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.text_handler))

    print("🚀 SaaS RUNNING")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
