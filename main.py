import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing")

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    durian_api TEXT,
    status TEXT DEFAULT 'off'
)
""")
conn.commit()

# ======================
# START
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # التأكد من وجود المستخدم
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    # حفظ التوكن
    if text.startswith("🔑"):
        context.user_data["step"] = "token"
        await update.message.reply_text("أرسل توكن البوت الآن")
        return

    # حفظ Durian API
    if text.startswith("🌐"):
        context.user_data["step"] = "api"
        await update.message.reply_text("أرسل API الخاص بـ Durian")
        return

    # استقبال البيانات
    step = context.user_data.get("step")

    if step == "token":
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")

    elif step == "api":
        cursor.execute("UPDATE users SET durian_api=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ API")

    elif text == "▶ تشغيل البوت":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم التشغيل")

    elif text == "⏹ إيقاف البوت":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم الإيقاف")

    elif text == "📊 الحالة":
        cursor.execute("SELECT bot_token, durian_api, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        await update.message.reply_text(
            f"""📊 الحالة:
توكن: {'موجود' if data and data[0] else 'غير موجود'}
Durian: {'موجود' if data and data[1] else 'غير موجود'}
الحالة: {data[2] if data else 'off'}"""
        )
