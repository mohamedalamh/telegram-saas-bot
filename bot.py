from telegram import Update
from telegram.ext import ContextTypes
import database as db
from keyboards import main_menu


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    db.add_user(user.id, user.username)

    await update.message.reply_text(
        "🚀 أهلاً بك في النظام الاحترافي",
        reply_markup=main_menu()
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    # ➕ ADD TOKEN
    if data == "add_token":
        context.user_data["step"] = "token"
        await q.message.reply_text("📥 أرسل التوكن")

    # 🌍 API USER
    elif data == "add_api_user":
        context.user_data["step"] = "api_user"
        await q.message.reply_text("📥 أرسل اسم المستخدم في الموقع")

    # 🔑 API KEY
    elif data == "add_api_key":
        context.user_data["step"] = "api_key"
        await q.message.reply_text("📥 أرسل ApiKey")

    # 📡 CHANNEL ID
    elif data == "add_channel":
        context.user_data["step"] = "channel"
        await q.message.reply_text("📥 أرسل ID القناة")

    # 🚀 START
    elif data == "start_bot":
        db.set_status(q.from_user.id, "active")
        await q.message.reply_text("🚀 تم التشغيل")

    # ⛔ STOP
    elif data == "stop_bot":
        db.set_status(q.from_user.id, "stopped")
        await q.message.reply_text("⛔ تم الإيقاف")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    step = context.user_data.get("step")

    if step == "token":
        db.save_account(user_id, token=text)
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")

    elif step == "api_user":
        db.save_account(user_id, api_user=text)
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ اسم المستخدم")

    elif step == "api_key":
        db.save_account(user_id, api_key=text)
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ ApiKey")

    elif step == "channel":
        db.save_account(user_id, channel_id=text)
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ القناة")

    else:
        await update.message.reply_text("📌 استخدم الأزرار")
