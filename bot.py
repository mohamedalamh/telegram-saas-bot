from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import database as db

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.add_user(user_id)

    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌍 اختيار الدولة"],
        ["▶️ تشغيل البوت", "⛔ إيقاف البوت"],
        ["💳 الاشتراك"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    token = " ".join(context.args)

    if not token:
        await update.message.reply_text("❌ أرسل التوكن هكذا:\n/addtoken TOKEN")
        return

    db.update_token(user_id, token)
    await update.message.reply_text("✅ تم حفظ التوكن")
