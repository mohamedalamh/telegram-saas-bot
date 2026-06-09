import os
import sqlite3
import threading
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= TOKEN =================
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN is missing")

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    api TEXT,
    country TEXT,
    status TEXT DEFAULT 'off'
)
""")
conn.commit()

# ================= RUNNING BOTS =================
running_bots = {}
stop_flags = {}

# ================= USER BOT =================
def run_user_bot(user_id, bot_token):
    try:
        app = Application.builder().token(bot_token).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("🤖 بوتك يعمل الآن")

        app.add_handler(CommandHandler("start", start))

        print(f"🚀 Bot started for user {user_id}")

        # تشغيل مع مراقبة stop flag
        def runner():
            while not stop_flags.get(user_id, False):
                try:
                    app.run_polling(stop_signals=None)
                except Exception as e:
                    print("Bot error:", e)
                    time.sleep(2)

        runner()

    except Exception as e:
        print(f"Error bot {user_id}: {e}")

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌐 إضافة API"],
        ["🌍 الدولة"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في النظام المحسن",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= HANDLE =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    # ===== TOKEN =====
    if text == "🔑 إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن")
        return

    if step == "token":
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ التوكن")
        return

    # ===== API =====
    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API")
        return

    if step == "api":
        cursor.execute("UPDATE users SET api=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ API")
        return

    # ===== COUNTRY =====
    if text == "🌍 الدولة":
        context.user_data["step"] = "country"
        await update.message.reply_text("📩 أرسل الدولة")
        return

    if step == "country":
        cursor.execute("UPDATE users SET country=? WHERE user_id=?", (text, user_id))
        conn.commit()
        context.user_data["step"] = None
        await update.message.reply_text("✅ تم حفظ الدولة")
        return

    # ===== START BOT =====
    if text == "▶ تشغيل البوت":
        cursor.execute("SELECT bot_token FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        if not data or not data[0]:
            await update.message.reply_text("❌ لا يوجد توكن")
            return

        if user_id in running_bots:
            await update.message.reply_text("⚠️ البوت يعمل بالفعل")
            return

        stop_flags[user_id] = False

        thread = threading.Thread(target=run_user_bot, args=(user_id, data[0]))
        thread.start()

        running_bots[user_id] = thread

        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("🟢 تم التشغيل")
        return

    # ===== STOP BOT =====
    if text == "⏹ إيقاف البوت":
        stop_flags[user_id] = True
        running_bots.pop(user_id, None)

        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("🔴 تم الإيقاف (محسن)")
        return

    # ===== STATUS =====
    if text == "📊 الحالة":
        cursor.execute("SELECT bot_token, api, country, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        await update.message.reply_text(f"""
📊 الحالة:

🔑 التوكن: {"موجود" if data and data[0] else "غير موجود"}
🌐 API: {"موجود" if data and data[1] else "غير موجود"}
🌍 الدولة: {data[2] if data and data[2] else "غير محدد"}
⚙ الحالة: {data[3] if data else "off"}
""")

# ================= MAIN BOT =================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 MAIN BOT RUNNING")
app.run_polling()
