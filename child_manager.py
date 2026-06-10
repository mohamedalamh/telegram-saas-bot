import asyncio
from telegram.ext import Application, CommandHandler

from database import set_status

running_bots = {}


async def child_start(update, context):
    await update.message.reply_text("🤖 تم تشغيل البوت بنجاح")


async def run_bot_instance(user_id, token):

    app = Application.builder().token(token).build()

    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", child_start))

    set_status(user_id, "running")

    print(f"[BOT STARTED] user_id={user_id}")

    await app.run_polling(close_loop=False)


def start_bot(user_id, token, loop):

    if user_id in running_bots:
        return False

    task = loop.create_task(run_bot_instance(user_id, token))

    running_bots[user_id] = task

    return True


def stop_bot(user_id):

    task = running_bots.get(user_id)

    if task:
        task.cancel()
        del running_bots[user_id]

    set_status(user_id, "stopped")

    return True
