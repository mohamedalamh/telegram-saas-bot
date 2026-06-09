from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu
import database as db


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    db.add_user(user.id, user.username)

    await update.message.reply_text(
        "👋 أهلاً بك في النظام\nاختر من القائمة:",
        reply_markup=main_menu()
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "add_token":
        context.user_data["wait_token"] = True
        await query.message.reply_text("📥 أرسل توكن البوت الآن:")

    elif data == "start_bot":
        await query.message.reply_text("🚀 تشغيل البوت")

    elif data == "stop_bot":
        await query.message.reply_text("⛔ إيقاف البوت")

    elif data == "settings":
        await query.message.reply_text("⚙️ الإعدادات")

    elif data == "subscription":
        await query.message.reply_text("💳 الاشتراك")


# ---------------- TEXT HANDLER ----------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # استقبال التوكن
    if context.user_data.get("wait_token"):

        db.save_token(update.effective_user.id, text)

        context.user_data["wait_token"] = False

        await update.message.reply_text("✅ تم حفظ التوكن بنجاح")
        return

    await update.message.reply_text("📌 استخدم الأزرار فقط")
