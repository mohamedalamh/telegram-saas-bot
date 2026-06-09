import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import bot

TOKEN = os.getenv("BOT_TOKEN")

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN missing in environment variables")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.button))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
