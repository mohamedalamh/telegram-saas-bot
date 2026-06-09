import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔑 توكن البوت"],
        ["🌐 بيانات Durian"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة", "💎 الاشتراك"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في البوت الرئيسي",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot Started...")
app.run_polling()
