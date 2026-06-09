import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌐 إضافة API"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة", "💎 الاشتراك"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك، البوت يعمل الآن",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✔ تم استلام رسالتك")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Bot is running...")
app.run_polling()
