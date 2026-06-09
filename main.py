import os
from telegram.ext import Application

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

print("🚀 Bot is running...")

app = Application.builder().token(TOKEN).build()
app.run_polling()
