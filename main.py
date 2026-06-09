import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

ADMIN_TOKEN = os.getenv("BOT_TOKEN")

if not ADMIN_TOKEN:
    raise Exception("BOT_TOKEN missing in Railway Variables")

# تخزين مؤقت (لاحقًا نطورها لقاعدة بيانات)
user_tokens = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ إضافة توكن"],
        ["📊 عرض التوكن"],
        ["⛔ حذف التوكن"],
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في النظام",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "➕ إضافة توكن":
        await update.message.reply_text("أرسل توكن البوت الخاص بك الآن:")
        context.user_data["awaiting_token"] = True

    elif context.user_data.get("awaiting_token"):
        user_tokens[user_id] = text
        context.user_data["awaiting_token"] = False
        await update.message.reply_text("✅ تم حفظ التوكن بنجاح")

    elif text == "📊 عرض التوكن":
        token = user_tokens.get(user_id)
        await update.message.reply_text(f"توكنك: {token}" if token else "لا يوجد توكن")

    elif text == "⛔ حذف التوكن":
        user_tokens.pop(user_id, None)
        await update.message.reply_text("تم حذف التوكن")

app = Application.builder().token(ADMIN_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
