import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

user_tokens = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ إضافة توكن"],
        ["📊 عرض التوكن"],
        ["⛔ حذف التوكن"],
    ]

    await update.message.reply_text(
        "👋 أهلاً بك",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "➕ إضافة توكن":
        await update.message.reply_text("أرسل التوكن:")
        context.user_data["wait"] = True

    elif context.user_data.get("wait"):
        user_tokens[user_id] = text
        context.user_data["wait"] = False
        await update.message.reply_text("تم حفظ التوكن")

    elif text == "📊 عرض التوكن":
        await update.message.reply_text(user_tokens.get(user_id, "لا يوجد"))

    elif text == "⛔ حذف التوكن":
        user_tokens.pop(user_id, None)
        await update.message.reply_text("تم الحذف")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")
app.run_polling()
