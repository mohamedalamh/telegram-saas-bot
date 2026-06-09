import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# تخزين البوتات في الذاكرة
USER_BOTS = {}

MASTER_TOKEN = os.getenv("BOT_TOKEN")

if not MASTER_TOKEN:
    raise Exception("BOT_TOKEN missing")

# تشغيل بوت مستخدم
def start_user_bot(user_id: str, token: str):
    async def run_bot():
        app = Application.builder().token(token).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("👋 بوتك يعمل الآن بنجاح")

        app.add_handler(CommandHandler("start", start))
        await app.run_polling()

    loop = asyncio.get_event_loop()
    task = loop.create_task(run_bot())
    USER_BOTS[user_id] = task


# لوحة البوت الرئيسي
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ إضافة توكن"],
        ["▶ تشغيل بوتي"],
        ["⏹ إيقاف بوتي"],
        ["📊 حالتي"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# استقبال الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.chat_id)

    # إضافة التوكن
    if text == "➕ إضافة توكن":
        await update.message.reply_text("أرسل توكن البوت الآن:")
        context.user_data["await_token"] = True
        return

    # استقبال التوكن
    if context.user_data.get("await_token"):
        context.user_data["token"] = text
        context.user_data["await_token"] = False
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    # تشغيل بوت المستخدم
    if text == "▶ تشغيل بوتي":
        token = context.user_data.get("token")

        if not token:
            await update.message.reply_text("❌ لم تضف توكن بعد")
            return

        if user_id in USER_BOTS:
            await update.message.reply_text("⚠️ البوت يعمل بالفعل")
            return

        start_user_bot(user_id, token)
        await update.message.reply_text("🚀 تم تشغيل بوتك")

    # إيقاف بوت المستخدم
    if text == "⏹ إيقاف بوتي":
        task = USER_BOTS.get(user_id)
        if task:
            task.cancel()
            del USER_BOTS[user_id]
            await update.message.reply_text("🛑 تم الإيقاف")
        else:
            await update.message.reply_text("❌ لا يوجد بوت يعمل")


def main():
    app = Application.builder().token(MASTER_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("message", handle_message))

    app.add_handler(
        CommandHandler("text", handle_message)
    )

    print("Master Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
