import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    durian_api TEXT,
    status TEXT DEFAULT 'inactive'
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
        ["➕ إضافة توكن"],
        ["🌐 إضافة API"],
        ["▶ تشغيل النظام", "⏹ إيقاف النظام"],
        ["📊 لوحة التحكم"]
    ]

    await update.message.reply_text(
        "🚀 مرحبًا بك في منصة SaaS Bot",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ======================
# HANDLER ENGINE
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    step = context.user_data.get("step")

    # اختيار التوكن
    if text == "➕ إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل توكن البوت")
        return

    # اختيار API
    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API الخاص بك")
        return

    # إدخال التوكن
    if step == "token":
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    # إدخال API
    if step == "api":
        cursor.execute("UPDATE users SET durian_api=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ API")
        return

    # تشغيل النظام
    if text == "▶ تشغيل النظام":
        cursor.execute("UPDATE users SET status='active' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 النظام يعمل الآن")
        return

    # إيقاف النظام
    if text == "⏹ إيقاف النظام":
        cursor.execute("UPDATE users SET status='inactive' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم إيقاف النظام")
        return

    # لوحة التحكم
    if text == "📊 لوحة التحكم":
        cursor.execute("SELECT bot_token, durian_api, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        await update.message.reply_text(f"""
📊 لوحة التحكم:

🔑 التوكن: {'موجود' if data and data[0] else 'غير موجود'}
🌐 API: {'موجود' if data and data[1] else 'غير موجود'}
⚙ الحالة: {data[2] if data else 'inactive'}
        """)

# ======================
# RUN BOT
# ======================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 SaaS Bot Running")
app.run_polling()
