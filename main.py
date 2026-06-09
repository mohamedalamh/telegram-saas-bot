import os
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

import bot

# إعداد اللوق حتى تعرف الخطأ لو حصل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")


def main():

    # 🔴 حماية: إذا التوكن غير موجود
    if not TOKEN:
        print("❌ BOT_TOKEN غير موجود في Environment Variables")
        return

    # 🚀 بناء التطبيق
    app = Application.builder().token(TOKEN).build()

    # =========================
    # 🎯 الأوامر الأساسية
    # =========================
    app.add_handler(CommandHandler("start", bot.start))

    # =========================
    # 🎯 الأزرار (Inline Buttons)
    # =========================
    app.add_handler(CallbackQueryHandler(bot.button))

    # =========================
    # 🎯 استقبال الرسائل النصية
    # =========================
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.text_handler))

    # =========================
    # 🚀 تشغيل البوت
    # =========================
    print("🚀 Bot is running safely...")

    try:
        app.run_polling(
            drop_pending_updates=True  # يمنع التعليق من رسائل قديمة
        )
    except Exception as e:
        print("❌ Bot crashed:", e)


if __name__ == "__main__":
    main()
