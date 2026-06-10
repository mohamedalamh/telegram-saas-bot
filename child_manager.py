import asyncio
from telegram.ext import Application, CommandHandler

from database import set_status

# نخزن التطبيقات بدل threads
running_apps = {}


async def child_start(update, context):
    await update.message.reply_text("🤖 تم تشغيل البوت بنجاح")


async def run_app(user_id, token):

    app = Application.builder().token(token).build()

    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", child_start))

    set_status(user_id, "running")

    print(f"[STARTED] user_id={user_id}")

    try:
        await app.run_polling(close_loop=False)
    except asyncio.CancelledError:
        print(f"[STOPPED] user_id={user_id}")
    finally:
        await app.shutdown()


def start_bot(user_id, token, loop):

    if user_id in running_apps:
        return False

    task = loop.create_task(run_app(user_id, token))

    running_apps[user_id] = {
        "task": task
    }

    return True


def stop_bot(user_id):

    bot = running_apps.get(user_id)

    if not bot:
        return False

    task = bot["task"]

    task.cancel()

    running_apps.pop(user_id, None)

    set_status(user_id, "stopped")

    return True
