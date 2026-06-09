import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler

import database as db


running_bots = {}


async def run_user_bot(user_id: int, token: str):

    if user_id in running_bots:
        return

    app = Application.builder().token(token).build()

    async def start(update, context):
        await update.message.reply_text("👋 بوتك يعمل الآن بنجاح")

    app.add_handler(CommandHandler("start", start))

    running_bots[user_id] = app

    print(f"🚀 Starting bot for user {user_id}")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # keep running
    while True:
        await asyncio.sleep(3600)


async def stop_user_bot(user_id: int):

    app = running_bots.get(user_id)

    if app:
        await app.stop()
        running_bots.pop(user_id, None)
