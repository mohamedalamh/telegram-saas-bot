import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

async def run_bot(token: str, user_id: int):

    app = Application.builder().token(token).build()

    async def start(update: Update, context):
        await update.message.reply_text("🚀 بوتك يعمل الآن بشكل احترافي")

    app.add_handler(CommandHandler("start", start))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print(f"Bot running for user {user_id}")

    # يبقى شغال
    await asyncio.Event().wait()
