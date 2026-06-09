from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("➕ إضافة توكن", callback_data="add")],
        [InlineKeyboardButton("▶️ تشغيل", callback_data="start")],
        [InlineKeyboardButton("⛔ إيقاف", callback_data="stop")]
    ]

    await update.message.reply_text(
        "👋 مرحباً بك في البوت",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add":
        await query.message.reply_text("📌 أرسل التوكن الآن")
    elif query.data == "start":
        await query.message.reply_text("🚀 تم التشغيل")
    elif query.data == "stop":
        await query.message.reply_text("⛔ تم الإيقاف")
