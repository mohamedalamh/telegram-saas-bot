from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start_user_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! هذا البوت مدار بالكامل عبر منصة SaaS.")

def create_user_app(token: str):
    """تنشئ نسخة تطبيق مستقلة لكل توكن"""
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    return app
