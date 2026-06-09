from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu
import database as db
async def start(update, context):

    user = update.effective_user

    db.add_user(user.id, user.username)

    await update.message.reply_text(
        "أهلاً بك 👋\nالنظام جاهز للعمل",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "add_token":
    await query.message.reply_text("أرسل توكن البوت الآن")
    context.user_data["wait_token"] = True

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
async def text_handler(update, context):

    user_id = update.effective_user.id
    text = update.message.text

    # استقبال التوكن
    if context.user_data.get("wait_token"):

        db.save_bot(user_id, text)

        context.user_data["wait_token"] = False

        await update.message.reply_text(
            "✅ تم حفظ التوكن بنجاح"
        )
        return

    await update.message.reply_text(
        "استخدم الأزرار للتحكم 👇"
    )
