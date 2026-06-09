from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import database as db

ADMIN_ID = 123456789  # 🔴 ضع رقمك هنا

# 👋 البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.add_user(user_id)

    if user_id == ADMIN_ID:
        keyboard = [
            ["👥 المستخدمين"],
            ["💳 تفعيل اشتراك", "⛔ إيقاف اشتراك"]
        ]
        text = "👑 لوحة الأدمن"
    else:
        keyboard = [
            ["🔑 إضافة توكن"],
            ["▶️ تشغيل البوت", "⛔ إيقاف البوت"],
            ["💳 الاشتراك"]
        ]
        text = "👋 أهلاً بك في لوحة التحكم"

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 🔑 إضافة توكن
async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    token = " ".join(context.args)

    if not token:
        await update.message.reply_text("استخدم: /addtoken TOKEN")
        return

    db.update_token(user_id, token)
    await update.message.reply_text("✅ تم حفظ التوكن")

# ▶️ تشغيل
async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user or not user[1]:
        await update.message.reply_text("❌ أضف التوكن أولاً")
        return

    db.update_status(user_id, "active")
    await update.message.reply_text("🚀 تم تشغيل البوت")

# ⛔ إيقاف
async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_status(user_id, "inactive")
    await update.message.reply_text("⛔ تم إيقاف البوت")

# 👥 عرض المستخدمين (للأدمن فقط)
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    users = db.get_all_users()

    text = "👥 المستخدمين:\n\n"
    for u in users:
        text += f"ID: {u[0]} | Plan: {u[4]} | Status: {u[3]}\n"

    await update.message.reply_text(text)
