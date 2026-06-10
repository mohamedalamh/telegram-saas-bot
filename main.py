import os
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import database as db
import child_manager

from bot import start, button, text_handler


def main():

    db.init_db()

    TOKEN = os.getenv("MAIN_BOT_TOKEN")

    if not TOKEN:
        raise Exception("MAIN_BOT_TOKEN is not set in environment variables")

    # 🤖 إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()

    # 🔥 ربط الهاندلرز (مهم جدًا)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🚀 SAAS SYSTEM RUNNING")

    # 🔁 تشغيل البوتات الفرعية بعد تشغيل النظام
    async def post_init(app):
        child_manager.restore_bots(app.create_task)

    app.post_init = post_init

    # ▶ تشغيل البوت
    app.run_polling()


if __name__ == "__main__":
    main()
