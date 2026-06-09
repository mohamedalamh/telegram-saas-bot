import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ======================
# TOKEN
# ======================
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing in Railway Variables")

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["🔑 توكن البوت"],
        ["🌐 بيانات Durian"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في النظام الرئيسي",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ======================
# HANDLER
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # التأكد من المستخدم
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    waiting = context.user_data.get("waiting")

    # اختيار إدخال التوكن
    if text == "🔑 توكن البوت":
        context.user_data["waiting"] = "token"
        await update.message.reply_text("📩 أرسل توكن البوت الآن")
        return

    # اختيار إدخال API
    elif text == "🌐 بيانات Durian":
        context.user_data["waiting"] = "api"
        await update.message.reply_text("📩 أرسل API الخاص بـ Durian")
        return

    # استقبال التوكن
    elif waiting == "token":
        cursor.execute(
            "UPDATE users SET bot_token=? WHERE user_id=?",
            (text, user_id)
        )
        conn.commit()
        context.user_data["waiting"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    # استقبال API
    elif waiting == "api":
        cursor.execute(
            "UPDATE users SET durian_api=? WHERE user_id=?",
            (text, user_id)
        )
        conn.commit()
        context.user_data["waiting"] = None
        await update.message.reply_text("✅ تم حفظ API")
        return

    # تشغيل
    elif text == "▶ تشغيل البوت":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم تشغيل البوت")

    # إيقاف
    elif text == "⏹ إيقاف البوت":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم إيقاف البوت")

    # الحالة
    elif text == "📊 الحالة":
        cursor.execute(
            "SELECT bot_token, durian_api, status FROM users WHERE user_id=?",
            (user_id,)
        )
        row = cursor.fetchone()

        await update.message.reply_text(
            f"""📊 الحالة:
توكن: {'موجود' if row and row[0] else 'غير موجود'}
Durian: {'موجود' if row and row[1] else 'غير موجود'}
الحالة: {row[2] if row else 'off'}"""
        )

# ======================
# BOT START
# ======================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot Started Successfully 🚀")
app.run_polling()
