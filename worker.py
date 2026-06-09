import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

token = sys.argv[1]
user_id = sys.argv[2]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 بوتك شغال بنجاح (User {user_id})")

app = Application.builder().token(token).build()
app.add_handler(CommandHandler("start", start))

print(f"Worker running for {user_id}")
app.run_polling()
