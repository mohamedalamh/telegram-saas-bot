from telegram.ext import Application, CommandHandler

def run_user_bot(token):

    app = Application.builder().token(token).build()

    async def start(update, context):
        await update.message.reply_text("👋 بوتك شغال!")

    app.add_handler(CommandHandler("start", start))

    app.run_polling()
