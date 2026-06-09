from telegram import Update
from telegram.ext import ContextTypes
import database as db
import bot_manager as manager


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 أهلاً بك في نظام SaaS\nأرسل /menu"
    )


# BUTTONS
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "add_token":
        context.user_data["wait_token"] = True
        await query.message.reply_text("📥 أرسل توكن البوت الخاص بك")

    elif data == "start_bot":
        token = db.get_token(query.from_user.id)

        if token:
            await manager.run_user_bot(query.from_user.id, token)
            await query.message.reply_text("🚀 تم تشغيل بوتك")
        else:
            await query.message.reply_text("❌ لا يوجد توكن")

    elif data == "stop_bot":
        await manager.stop_user_bot(query.from_user.id)
        await query.message.reply_text("⛔ تم الإيقاف")


# TEXT HANDLER
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("wait_token"):

        db.save_token(update.effective_user.id, update.message.text)

        context.user_data["wait_token"] = False

        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    await update.message.reply_text("📌 استخدم الأزرار")
