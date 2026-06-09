import os
import sqlite3
import subprocess
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

ADMIN_ID = 123456789  # غيّره

MASTER_TOKEN = os.environ.get("BOT_TOKEN")

if not MASTER_TOKEN:
    raise Exception("BOT_TOKEN missing")

# ================= DATABASE =================
conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    api TEXT,
    status TEXT DEFAULT 'off',
    process_id INTEGER
)
""")
conn.commit()

# ================= WORKER MANAGER =================
def start_bot_process(token, user_id):
    """
    تشغيل بوت المستخدم كـ Process مستقل
    """
    process = subprocess.Popen([
        "python", "worker.py",
        token,
        str(user_id)
    ])
    return process.pid

def stop_bot_process(pid):
    try:
        os.kill(pid, 9)
    except:
        pass

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["➕ إضافة توكن"],
        ["🌐 إضافة API"],
        ["▶ تشغيل البوت"],
        ["⏹ إيقاف البوت"],
        ["📊 الحالة"]
    ]

    if user_id == ADMIN_ID:
        keyboard.append(["⚙ لوحة الإدارة"])

    await update.message.reply_text(
        "👑 SaaS Control Panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    # ADD TOKEN
    if text == "➕ إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن")
        return

    # ADD API
    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API")
        return

    # SAVE TOKEN
    if step == "token":
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    # SAVE API
    if step == "api":
        cursor.execute("UPDATE users SET api=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ API")
        return

    # START BOT
    if text == "▶ تشغيل البوت":

        cursor.execute("SELECT bot_token FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if not row or not row[0]:
            await update.message.reply_text("❌ أضف التوكن أولاً")
            return

        token = row[0]

        process = subprocess.Popen([
            "python", "worker.py", token, str(user_id)
        ])

        cursor.execute(
            "UPDATE users SET status='on', process_id=? WHERE user_id=?",
            (process.pid, user_id)
        )
        conn.commit()

        await update.message.reply_text("🟢 تم تشغيل البوت فعلياً")

    # STOP BOT
    if text == "⏹ إيقاف البوت":

        cursor.execute("SELECT process_id FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if row and row[0]:
            stop_bot_process(row[0])

        cursor.execute("UPDATE users SET status='off', process_id=NULL WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("🔴 تم الإيقاف")

    # STATUS
    if text == "📊 الحالة":
        cursor.execute("SELECT status, bot_token, api FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        await update.message.reply_text(f"""
📊 الحالة:

⚙ Status: {row[0]}
🔑 Token: {'موجود' if row[1] else 'غير موجود'}
🌐 API: {'موجود' if row[2] else 'غير موجود'}
""")

# ================= RUN =================
app = Application.builder().token(MASTER_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 MASTER BOT RUNNING")
app.run_polling()
