from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "أهلاً بك في النظام",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "add_token":
        await query.message.reply_text(
            "أرسل توكن البوت"
        )

    elif query.data == "start_bot":
        await query.message.reply_text(
            "سيتم تشغيل البوت"
        )

    elif query.data == "stop_bot":
        await query.message.reply_text(
            "سيتم إيقاف البوت"
        )

    elif query.data == "settings":
        await query.message.reply_text(
            "الإعدادات"
        )

    elif query.data == "subscription":
        await query.message.reply_text(
            "معلومات الاشتراك"
        )
