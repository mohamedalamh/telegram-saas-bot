import os
from telegram.ext import Application

TOKEN = os.getenv("BOT_TOKEN")

print("🚀 Bot is starting...")

if not TOKEN:
    print("❌ BOT_TOKEN missing")
    exit()

app = Application.builder().token(TOKEN).build()

print("✅ Bot is running")
app.run_polling()
