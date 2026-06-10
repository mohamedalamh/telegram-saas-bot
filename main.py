import os
import asyncio
from telegram.ext import Application

import database as db
import child_manager

from bot import start, button, text_handler


def main():

    db.init_db()

    # ✅ أخذ التوكن من Railway Variables
    TOKEN = os.getenv("MAIN_BOT_TOKEN")

    if not TOKEN:
        raise Exception("MAIN_BOT_TOKEN is not set in environment variables")

    app = Application.builder().token(TOKEN).build()

    # ⚡ مهم جدًا في Python 3.13
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 🔁 تشغيل البوتات المحفوظة
    child_manager.restore_bots(loop)

    print("🚀 SAAS SYSTEM RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()
