from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu
import database as db
import bot_manager as manager


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    db.add_user(user.id, user.username)

    await update.message.reply_text(
        "👋 أهلاً بك في النظام",
        reply_markup=main_menu()   # 🔥 هذا أهم شيء
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    print("BUTTON CLICKED:", data)  # 🔥 للتأكد

    if data == "add_token":
        context.user_data["wait_token"] = True
        await query.message.reply_text("📥 أرسل التوكن الآن")

    elif data == "start_bot":
        token = db.get_token(query.from_user.id)

        if not token:
            await query.message.reply_text("❌ لا يوجد توكن")
            return

        await manager.run_user_bot(query.from_user.id, token)
        await query.message.reply_text("🚀 تم التشغيل")

    elif data == "stop_bot":
        await manager.stop_user_bot(query.from_user.id)
        await query.message.reply_text("⛔ تم الإيقاف")


# ---------------- TEXT ----------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("wait_token"):
        db.save_token(update.effective_user.id, update.message.text)
        context.user_data["wait_token"] = False
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    await update.message.reply_text("📌 استخدم الأزرار فقط")
