import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌐 إضافة API"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في النظام",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

print("Bot Running...")
app.run_polling()
