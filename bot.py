from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
import durian_api as api


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("➕ توكن", callback_data="token")],
        [InlineKeyboardButton("🌍 API إعداد", callback_data="api")],
        [InlineKeyboardButton("📡 قناة", callback_data="channel")],
        [InlineKeyboardButton("🌎 دولة", callback_data="country")],
        [InlineKeyboardButton("▶ تشغيل", callback_data="start")],
        [InlineKeyboardButton("⛔ إيقاف", callback_data="stop")],
    ]

    await update.message.reply_text(
        "🔥 نظام SaaS جاهز",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# CALLBACK
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    if q.data == "token":
        context.user_data["step"] = "token"
        await q.message.reply_text("أرسل التوكن")

    elif q.data == "api":
        context.user_data["step"] = "api_name"
        await q.message.reply_text("أرسل اسم API")

    elif q.data == "channel":
        context.user_data["step"] = "channel"
        await q.message.reply_text("أرسل ID القناة")

    elif q.data == "country":
        context.user_data["step"] = "country"
        await q.message.reply_text("أرسل رمز الدولة (مثال: us)")

    elif q.data == "start":
        db.set_status(uid, "active")
        await q.message.reply_text("🚀 تم التشغيل")

    elif q.data == "stop":
        db.set_status(uid, "inactive")
        await q.message.reply_text("⛔ تم الإيقاف")


# TEXT HANDLER
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    step = context.user_data.get("step")

    if step == "token":
        db.update_token(uid, text)
        await update.message.reply_text("✔ تم حفظ التوكن")
        context.user_data["step"] = None

    elif step == "api_name":
        context.user_data["api_name"] = text
        context.user_data["step"] = "api_key"
        await update.message.reply_text("أرسل API KEY")

    elif step == "api_key":
        name = context.user_data.get("api_name")
        db.update_api(uid, name, text)
        context.user_data["step"] = None
        await update.message.reply_text("✔ تم حفظ API")

    elif step == "channel":
        db.update_channel(uid, text)
        context.user_data["step"] = None
        await update.message.reply_text("✔ تم حفظ القناة")

    elif step == "country":
        db.update_country(uid, text)
        context.user_data["step"] = None
        await update.message.reply_text("✔ تم حفظ الدولة")
