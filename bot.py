from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu

import database as db
import child_manager

WAITING_TOKEN = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 أهلاً بك في لوحة التحكم",
        reply_markup=main_menu()
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if query.data == "add_token":

        WAITING_TOKEN[user_id] = True

        await query.message.reply_text(
            "🔑 أرسل توكن البوت"
        )

    elif query.data == "start_bot":

        token = db.get_token(user_id)

        if not token:
            await query.message.reply_text(
                "❌ أضف التوكن أولاً"
            )
            return

        result = child_manager.start_bot(
            user_id,
            token
        )

        if result:
            db.set_status(user_id, 1)

            await query.message.reply_text(
                "✅ تم تشغيل البوت"
            )

    elif query.data == "stop_bot":

        result = child_manager.stop_bot(user_id)

        if result:
            db.set_status(user_id, 0)

            await query.message.reply_text(
                "❌ تم إيقاف البوت"
            )

    elif query.data == "status":

        status = db.get_status(user_id)

        text = "🟢 يعمل" if status else "🔴 متوقف"

        await query.message.reply_text(
            f"حالة البوت: {text}"
        )

    elif query.data == "support":

        await query.message.reply_text(
            "📞 تواصل مع الدعم"
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in WAITING_TOKEN:

        token = update.message.text.strip()

        db.save_token(
            user_id,
            token
        )

        del WAITING_TOKEN[user_id]

        await update.message.reply_text(
            "✅ تم حفظ التوكن بنجاح"
        )
