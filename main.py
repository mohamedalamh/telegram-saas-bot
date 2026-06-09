import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import bot
import database

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


def main():
    if not TOKEN:
        print("BOT_TOKEN missing")
        return

    # تهيئة قاعدة البيانات
    database.init_db()

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", bot.start))

    # Buttons
    app.add_handler(CallbackQueryHandler(bot.button))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.text_handler))

    print("🚀 Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
