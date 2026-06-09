import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تفعيل التسجيل
logging.basicConfig(level=logging.INFO)

# قراءة التوكن من المتغيرات البيئية
TOKEN = os.environ.get('MAIN_BOT_TOKEN')

if not TOKEN:
    raise ValueError("الرجاء تعيين MAIN_BOT_TOKEN في متغيرات البيئة")

# تعريف أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 البوت يعمل بنجاح!\n\n"
        "أرسل /help للمساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة"
    )

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 البوت يعمل... اضغط Ctrl+C للإيقاف")
    app.run_polling()

if __name__ == "__main__":
    main()
