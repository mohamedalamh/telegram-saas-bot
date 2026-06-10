from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu
import database as db
import child_manager
import asyncio

WAITING_TOKEN = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم",
        reply_markup=main_menu()
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # نحصل على event loop الحالي (مهم جدًا)
    loop = asyncio.get_running_loop()

    if query.data == "add_token":

        WAITING_TOKEN[user_id] = True

        await query.message.reply_text("🔑 أرسل توكن البوت")


    elif query.data == "start_bot":

        user = db.get_user(user_id)

        if not user or not user[1]:
            await query.message.reply_text("❌ أضف التوكن أولاً")
            return

        token = user[1]

        result = child_manager.start_bot(user_id, token, loop)

        if result:
            db.set_status(user_id, "running")
            await query.message.reply_text("✅ تم تشغيل البوت")
        else:
            await query.message.reply_text("⚠️ البوت يعمل بالفعل")


    elif query.data == "stop_bot":

        result = child_manager.stop_bot(user_id)

        if result:
            db.set_status(user_id, "stopped")
            await query.message.reply_text("❌ تم إيقاف البوت")
        else:
            await query.message.reply_text("⚠️ البوت غير شغال")


    elif query.data == "status":

        user = db.get_user(user_id)

        if not user:
            await query.message.reply_text("❌ لا يوجد بوت")
            return

        status = user[2]

        text = "🟢 يعمل" if status == "running" else "🔴 متوقف"

        await query.message.reply_text(f"حالة البوت: {text}")


    elif query.data == "support":

        await query.message.reply_text("📞 تواصل مع الدعم")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in WAITING_TOKEN:

        token = update.message.text.strip()

        db.set_token(user_id, token)

        del WAITING_TOKEN[user_id]

        await update.message.reply_text("✅ تم حفظ التوكن بنجاح")
