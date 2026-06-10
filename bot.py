from telegram import Update
from telegram.ext import ContextTypes
import asyncio

from keyboards import main_menu
import database as db
import child_manager

WAITING_TOKEN = set()
LOOP = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم",
        reply_markup=main_menu()
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global LOOP

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if LOOP is None:
        LOOP = asyncio.get_running_loop()

    # ➕ إضافة توكن
    if query.data == "add_token":
        WAITING_TOKEN.add(user_id)
        await query.message.reply_text("🔑 أرسل التوكن")

    # ▶ تشغيل بوت
    elif query.data == "start_bot":

        user = db.get_user(user_id)

        if not user or not user[1]:
            await query.message.reply_text("❌ أضف التوكن أولاً")
            return

        token = user[1]

        ok = child_manager.start_bot(user_id, token, LOOP)

        if ok:
            db.set_status(user_id, "running")
            await query.message.reply_text("✅ تم التشغيل")
        else:
            await query.message.reply_text("⚠️ البوت يعمل بالفعل")

    # ⛔ إيقاف بوت
    elif query.data == "stop_bot":

        ok = child_manager.stop_bot(user_id)

        if ok:
            db.set_status(user_id, "stopped")
            await query.message.reply_text("❌ تم الإيقاف")
        else:
            await query.message.reply_text("⚠️ غير شغال")

    # 📊 حالة
    elif query.data == "status":

        user = db.get_user(user_id)

        if not user:
            await query.message.reply_text("❌ لا يوجد بوت")
            return

        status = user[2]

        text = "🟢 يعمل" if status == "running" else "🔴 متوقف"

        await query.message.reply_text(f"الحالة: {text}")

    # 📞 دعم
    elif query.data == "support":
        await query.message.reply_text("📞 تواصل مع الدعم")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in WAITING_TOKEN:

        token = update.message.text.strip()

        db.set_token(user_id, token)

        WAITING_TOKEN.remove(user_id)

        await update.message.reply_text("✅ تم حفظ التوكن")
