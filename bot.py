from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database

ADMIN_ID = 123456789  # ضع ايديك هنا

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("👥 المستخدمين", callback_data="users")],
            [InlineKeyboardButton("➕ إضافة مستخدم", callback_data="add_user")]
        ]
        text = "👑 لوحة الأدمن"
    else:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
            [InlineKeyboardButton("▶️ تشغيل", callback_data="start_bot")],
            [InlineKeyboardButton("⛔ إيقاف", callback_data="stop_bot")]
        ]
        text = "👤 لوحة المستخدم"

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "users":
        await query.message.reply_text(f"👥 عدد المستخدمين: {len(database.users)}")

    elif data == "add_user":
        await query.message.reply_text("📌 أرسل ايدي المستخدم")
        context.user_data["add_user"] = True

    elif data == "add_token":
        await query.message.reply_text("📌 أرسل التوكن")

    elif data == "start_bot":
        await query.message.reply_text("🚀 تم التشغيل")

    elif data == "stop_bot":
        await query.message.reply_text("⛔ تم الإيقاف")


# استقبال رسائل النص
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get("add_user"):
        database.users[int(text)] = {"active": True}
        context.user_data["add_user"] = False
        await update.message.reply_text("✅ تم إضافة المستخدم")
