import asyncio
from telegram.ext import Application, CommandHandler

from database import set_status, get_running_users

# نخزن tasks فقط
running_tasks = {}


async def start_cmd(update, context):
    await update.message.reply_text("🤖 بوتك يعمل بنجاح")


async def run_bot(user_id, token):

    app = Application.builder().token(token).build()

    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", start_cmd))

    set_status(user_id, "running")

    print(f"✅ BOT STARTED: {user_id}")

    try:
        await app.run_polling(close_loop=False)
    except asyncio.CancelledError:
        pass
    finally:
        await app.shutdown()


# ▶ تشغيل بوت
def start_bot(user_id, token, loop):

    if user_id in running_tasks:
        return False

    task = loop.create_task(run_bot(user_id, token))

    running_tasks[user_id] = task

    return True


# ⛔ إيقاف بوت (حقيقي)
def stop_bot(user_id):

    task = running_tasks.get(user_id)

    if task:
        task.cancel()
        running_tasks.pop(user_id, None)

    set_status(user_id, "stopped")

    return True


# 🔁 استرجاع تلقائي بعد إعادة تشغيل السيرفر
def restore_bots(loop):

    users = get_running_users()

    for user_id, token in users:
        start_bot(user_id, token, loop)
