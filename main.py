import os
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

import bot

TOKEN = os.getenv("BOT_TOKEN")


def main():

    if not TOKEN:
        print("❌ BOT_TOKEN missing")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.text))

    print("🚀 SaaS Bot Running Fully Inside Telegram")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
