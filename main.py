import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from db import save_token, get_token, set_status, get_status
from worker import run_bot

ADMIN_TOKEN = "PUT_YOUR_ADMIN_BOT_TOKEN"

bots_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ إضافة توكن"],
        ["▶ تشغيل بوت"],
        ["⏹ إيقاف بوت"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👑 لوحة التحكم الاحترافية",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "➕ إضافة توكن":
        await update.message.reply_text("أرسل التوكن الآن")
        context.user_data["wait"] = True

    elif context.user_data.get("wait"):
        save_token(user_id, text)
        context.user_data["wait"] = False
        await update.message.reply_text("تم حفظ التوكن ✔")

    elif text == "▶ تشغيل بوت":
        token = get_token(user_id)

        if not token:
            await update.message.reply_text("أضف التوكن أولاً")
            return

        if user_id in bots_tasks:
            await update.message.reply_text("البوت يعمل بالفعل")
            return

        task = asyncio.create_task(run_bot(token, user_id))
        bots_tasks[user_id] = task

        set_status(user_id, "running")
        await update.message.reply_text("🚀 تم تشغيل البوت")

    elif text == "⏹ إيقاف بوت":
        task = bots_tasks.get(user_id)

        if task:
            task.cancel()
            del bots_tasks[user_id]
            set_status(user_id, "stopped")
            await update.message.reply_text("⛔ تم الإيقاف")
        else:
            await update.message.reply_text("لا يوجد بوت شغال")

    elif text == "📊 الحالة":
        status = get_status(user_id)
        await update.message.reply_text(f"الحالة: {status}")

app = Application.builder().token(ADMIN_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 System Running Professional SaaS Bot")
app.run_polling()
