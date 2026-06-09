import threading
from telegram import Bot
from telegram.ext import Application, CommandHandler

from database import get_user, set_status

# نخزن البوتات المشغلة في الذاكرة
running_bots = {}


# رسالة البوت الفرعي
async def child_start(update, context):
    await update.message.reply_text("مرحبا بك في بوتك الخاص 🤖")


def run_bot_instance(user_id, token):
    """
    تشغيل بوت فرعي فعلي (Polling)
    """

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", child_start))

    # تشغيل البوت
    print(f"[BOT STARTED] user_id={user_id}")

    app.run_polling()


def start_child(user_id):
    data = get_user(user_id)

    if not data or not data[1]:
        return "no_token"

    if user_id in running_bots:
        return "already_running"

    token = data[1]

    thread = threading.Thread(
        target=run_bot_instance,
        args=(user_id, token),
        daemon=True
    )

    running_bots[user_id] = thread
    thread.start()

    set_status(user_id, "running")

    return "started"


def stop_child(user_id):
    """
    ملاحظة مهمة:
    python-telegram-bot لا يدعم إيقاف polling بسهولة داخل thread،
    لذلك سنسجل الحالة فقط (في المرحلة التالية سنضيف حل أقوى)
    """

    if user_id in running_bots:
        del running_bots[user_id]

    set_status(user_id, "stopped")

    return "stopped"
