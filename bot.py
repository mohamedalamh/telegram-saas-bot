from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    db.add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
        [InlineKeyboardButton("▶ تشغيل", callback_data="start_bot")],
        [InlineKeyboardButton("⛔ إيقاف", callback_data="stop_bot")],
        [InlineKeyboardButton("⚙ الإعدادات", callback_data="settings")],
        [InlineKeyboardButton("💳 الاشتراك", callback_data="subscription")]
    ]

    await update.message.reply_text(
        "أهلاً بك في النظام",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "add_token":
        context.user_data["step"] = "token"
        await query.message.reply_text("أرسل توكن البوت الآن")

    elif query.data == "start_bot":
        db.set_status(user_id, "active")
        await query.message.reply_text("تم تشغيل البوت ✅")

    elif query.data == "stop_bot":
        db.set_status(user_id, "inactive")
        await query.message.reply_text("تم إيقاف البوت ⛔")

    elif query.data == "settings":
        token = db.get_token(user_id)
        await query.message.reply_text(f"الإعدادات:\nToken: {token}")

    elif query.data == "subscription":
        await query.message.reply_text("نظام الاشتراك غير مفعّل بعد")


# استقبال النصوص (توكن)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if context.user_data.get("step") == "token":
        db.save_token(user.id, text)

        context.user_data["step"] = None

        await update.message.reply_text("تم حفظ التوكن بنجاح ✅")
    else:
        await update.message.reply_text("استخدم الأزرار 👇")
