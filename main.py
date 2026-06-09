import os
from telegram.ext import Application, CommandHandler
import bot

TOKEN = os.getenv("BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()

    # أوامر المستخدم
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("addtoken", bot.add_token))
    app.add_handler(CommandHandler("startbot", bot.start_bot))
    app.add_handler(CommandHandler("stopbot", bot.stop_bot))

    # أدمن
    app.add_handler(CommandHandler("users", bot.users_list))

    print("🚀 SaaS Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
