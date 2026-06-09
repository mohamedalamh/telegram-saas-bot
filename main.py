import os
import sqlite3
import threading
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= MAIN ADMIN BOT TOKEN =================
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

# ================= FUNCTION TO RUN USER BOT =================
def run_user_bot(user_id, bot_token):
    try:
        app = Application.builder().token(bot_token).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("🤖 بوتك يعمل الآن بنجاح")

        app.add_handler(CommandHandler("start", start))

        print(f"Bot started for user {user_id}")
        app.run_polling()

    except Exception as e:
        print(f"Error user bot {user_id}: {e}")

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
        "👋 أهلاً بك في النظام المتعدد",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================= HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    # ===== ADD TOKEN =====
    if text == "🔑 إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل توكن البوت الآن")
        return

    # ===== SAVE TOKEN =====
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

    # ===== START USER BOT =====
    if text == "▶ تشغيل البوت":
        cursor.execute("SELECT bot_token FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        if not data or not data[0]:
            await update.message.reply_text("❌ لم يتم إضافة التوكن")
            return

        bot_token = data[0]

        if user_id in running_bots:
            await update.message.reply_text("⚠️ البوت شغال بالفعل")
            return

        thread = threading.Thread(target=run_user_bot, args=(user_id, bot_token))
        thread.start()

        running_bots[user_id] = thread

        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("🟢 تم تشغيل بوتك")
        return

    # ===== STOP BOT =====
    if text == "⏹ إيقاف البوت":
        if user_id in running_bots:
            del running_bots[user_id]

        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("🔴 تم الإيقاف (ملاحظة: الإيقاف جزئي)")
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
