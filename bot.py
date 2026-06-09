from telegram import Update
from telegram.ext import ContextTypes
import database as db

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        db.add_user(user.id, user.username)
    except Exception as e:
        print("DB ERROR:", e)

    await update.message.reply_text(
        "👋 أهلاً بك في النظام\nاستخدم الأزرار للتحكم"
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    print("BUTTON CLICKED:", data)

    try:

        if data == "add_token":
            await query.message.reply_text("🔑 أرسل توكن البوت الآن")

        elif data == "start_bot":
            db.set_status(user_id, "active")
            await query.message.reply_text("🟢 تم تشغيل البوت")

        elif data == "stop_bot":
            db.set_status(user_id, "inactive")
            await query.message.reply_text("🔴 تم إيقاف البوت")

        elif data == "settings":
            await query.message.reply_text("⚙️ الإعدادات")

        elif data == "subscription":
            await query.message.reply_text("💳 الاشتراك: غير مفعّل")

    except Exception as e:
        print("BUTTON ERROR:", e)
        await query.message.reply_text("⚠️ حدث خطأ داخلي")


# ---------------- TEXT HANDLER ----------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # حفظ التوكن بعد "add_token"
    if text and len(text) > 30:
        db.save_token(user_id, text)
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    await update.message.reply_text("❌ أمر غير معروف")
