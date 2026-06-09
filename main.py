import os
from telegram.ext import Application, CommandHandler
from handlers.start import start
from handlers.create_bot import create_bot

TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("createbot", create_bot))

print("🚀 SaaS Bot Running")
app.run_polling()
