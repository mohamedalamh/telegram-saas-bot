from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu
import database as db


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # حفظ المستخدم في قاعدة البيانات
    db.add_user(user.id, user.username)

    await update.message.reply_text(
        "👋 أهلاً بك في النظام الاحترافي\nاختر من القائمة:",
        reply_markup=main_menu()
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # ➤ إضافة توكن
    if data == "add_token":
        await query.message.reply_text(
            "📥 أرسل توكن البوت الآن:"
        )
        context.user_data["wait_token"] = True


    # ➤ تشغيل البوت
    elif data == "start_bot":
        await query.message.reply_text(
            "🚀 سيتم تشغيل البوت (سيتم تطويرها لاحقاً)"
        )


    # ➤ إيقاف البوت
    elif data == "stop_bot":
        await query.message.reply_text(
            "⛔ سيتم إيقاف البوت (سيتم تطويرها لاحقاً)"
        )


    # ➤ الإعدادات
    elif data == "settings":
        await query.message.reply_text(
            "⚙️ الإعدادات قيد التطوير"
        )


    # ➤ الاشتراك
    elif data == "subscription":
        await query.message.reply_text(
            "💳 نظام الاشتراك قيد التطوير"
        )


# ---------------- TEXT HANDLER ----------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    text = update.message.text

    # ➤ استقبال التوكن
    if context.user_data.get("wait_token"):

        db.save_bot(user.id, text)

        context.user_data["wait_token"] = False

        await update.message.reply_text(
            "✅ تم حفظ التوكن بنجاح"
        )
        return


    # ➤ رد افتراضي
    await update.message.reply_text(
        "📌 استخدم الأزرار للتحكم بالنظام"
    )
