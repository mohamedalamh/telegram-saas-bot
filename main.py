import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔑 إضافة توكن"],
        ["▶ تشغيل"],
        ["⏹ إيقاف"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 النظام يعمل الآن",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
