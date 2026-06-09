import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import bot

TOKEN = os.getenv("BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("addtoken", bot.add_token))

    print("🚀 SaaS Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
