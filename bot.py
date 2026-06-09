from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
        [InlineKeyboardButton("▶️ تشغيل البوت", callback_data="start_bot")],
        [InlineKeyboardButton("⛔ إيقاف البوت", callback_data="stop_bot")],
        [InlineKeyboardButton("💳 الاشتراك", callback_data="subscription")]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم الرئيسية",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# أمر إضافة التوكن
async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 أرسل التوكن الآن:")


# التعامل مع الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "add_token":
        await query.message.reply_text("📌 أرسل توكن البوت الآن")
    
    elif data == "start_bot":
        await query.message.reply_text("🚀 تم تشغيل البوت بنجاح")
    
    elif data == "stop_bot":
        await query.message.reply_text("⛔ تم إيقاف البوت")
    
    elif data == "subscription":
        await query.message.reply_text("💳 اشتراكك: مجاني حالياً")
