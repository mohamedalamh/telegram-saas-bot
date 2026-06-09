from telegram import Update
from telegram.ext import ContextTypes
from storage import save_token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك في نظام البوتات")

async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = " ".join(context.args)

    if not token:
        await update.message.reply_text("أرسل التوكن هكذا: /addbot TOKEN")
        return

    save_token(update.effective_user.id, token)

    await update.message.reply_text("✅ تم حفظ التوكن")
