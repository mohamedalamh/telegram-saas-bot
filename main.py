import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔑 حطي التوكن هنا أو من Railway Variables
TOKEN = os.getenv("BOT_TOKEN")

# /start أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك! البوت يعمل بنجاح 🚀")

# تشغيل البوت
def main():
    print("🚀 Bot is starting...")

    if not TOKEN:
        print("❌ BOT_TOKEN غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
