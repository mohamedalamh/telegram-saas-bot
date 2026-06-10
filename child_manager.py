import threading
from telegram import Update
from telegram.ext import Application, CommandHandler

from database import get_user, set_status

running_bots = {}


async def child_start(update: Update, context):
    await update.message.reply_text("🤖 تم تشغيل البوت بنجاح")


def run_bot_instance(user_id, token):

    app = Application.builder().token(token).build()

    # 🔥 حل مشكلة Conflict
    app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", child_start))

    print(f"[STARTED BOT] user_id={user_id}")

    app.run_polling()


# ✅ تشغيل البوت
def start_bot(user_id, token):

    if user_id in running_bots:
        return False

    thread = threading.Thread(
        target=run_bot_instance,
        args=(user_id, token),
        daemon=True
    )

    running_bots[user_id] = thread
    thread.start()

    set_status(user_id, "running")

    return True


# ❌ إيقاف البوت (مبدئي)
def stop_bot(user_id):

    if user_id in running_bots:
        del running_bots[user_id]

    set_status(user_id, "stopped")

    return True
