import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= TOKEN =================
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing in Railway Variables")

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    token TEXT,
    api TEXT,
    country TEXT,
    status TEXT DEFAULT 'off'
)
""")
conn.commit()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌐 إضافة API"],
        ["🌍 اختيار الدولة"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في النظام النهائي",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= HANDLE =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    # ========= اختيار إدخال =========
    if text == "🔑 إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن الآن")
        return

    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل الـ API الآن")
        return

    if text == "🌍 اختيار الدولة":
        context.user_data["step"] = "country"
        await update.message.reply_text("📩 أرسل اسم الدولة")
        return

    # ========= حفظ البيانات =========
    if step == "token":
        cursor.execute("UPDATE users SET token=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    if step == "api":
        cursor.execute("UPDATE users SET api=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ API")
        return

    if step == "country":
        cursor.execute("UPDATE users SET country=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ الدولة")
        return

    # ========= تشغيل =========
    if text == "▶ تشغيل البوت":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم تشغيل النظام")
        return

    # ========= إيقاف =========
    if text == "⏹ إيقاف البوت":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم إيقاف النظام")
        return

    # ========= الحالة =========
    if text == "📊 الحالة":
        cursor.execute("SELECT token, api, country, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        if not data:
            await update.message.reply_text("❌ لا توجد بيانات")
            return

        await update.message.reply_text(f"""
📊 بياناتك:

🔑 التوكن: {"موجود" if data[0] else "غير موجود"}
🌐 API: {"موجود" if data[1] else "غير موجود"}
🌍 الدولة: {data[2] if data[2] else "غير محدد"}
⚙ الحالة: {data[3]}
""")

# ================= BOT RUN =================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 BOT IS RUNNING")
app.run_polling()
