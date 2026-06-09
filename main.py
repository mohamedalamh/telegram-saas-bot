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
# HANDLE BUTTONS (مبدئي)
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🔑 توكن البوت":
        await update.message.reply_text("أرسل توكن البوت الآن")
    
    elif text == "🌐 بيانات Durian":
        await update.message.reply_text("أرسل API الخاص بـ Durian")
    
    elif text == "▶ تشغيل البوت":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم تشغيل البوت")
    
    elif text == "⏹ إيقاف البوت":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم إيقاف البوت")

    elif text == "📊 الحالة":
        cursor.execute("SELECT bot_token, durian_api, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        await update.message.reply_text(
            f"""📊 الحالة:
توكن: {'موجود' if data and data[0] else 'غير موجود'}
Durian: {'موجود' if data and data[1] else 'غير موجود'}
الحالة: {data[2] if data else 'off'}"""
        )

# ======================
# BOT
# ======================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot Running...")
app.run_polling()
