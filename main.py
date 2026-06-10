import asyncio
from telegram.ext import Application

import database as db
import child_manager

from bot import start, button, text_handler


def main():

    db.init_db()

    app = Application.builder().token(TOKEN).build()

    loop = asyncio.get_event_loop()

    # 🔥 Auto Restore SaaS
    child_manager.restore_bots(loop)

    print("🚀 SAAS SYSTEM RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()
