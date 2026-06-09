import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import bot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing!")

def main():
    app = Application.builder().token(TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("addtoken", bot.addtoken))

    # أزرار
    app.add_handler(CallbackQueryHandler(bot.button))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
