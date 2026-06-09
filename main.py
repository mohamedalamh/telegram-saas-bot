import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    api TEXT,
    country TEXT,
    status TEXT DEFAULT 'off',
    subscription TEXT DEFAULT 'free'
)
""")
conn.commit()

ADMIN_ID = 123456789

# ================= ENGINE =================
def run_user_logic(user_id, text):
    """
    هنا مستقبل النظام:
    - API calls
    - AI requests
    - automation
    """
    cursor.execute("SELECT api FROM users WHERE user_id=?", (user_id,))
    api = cursor.fetchone()

    return f"📡 تم استقبال طلبك | API: {api[0] if api else 'none'}"


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["➕ توكن"],
        ["🌐 API"],
        ["🌍 دولة"],
        ["▶ تشغيل"],
        ["⏹ إيقاف"],
        ["💎 اشتراك"]
    ]

    if user_id == ADMIN_ID:
        keyboard.append(["⚙ لوحة الإدارة"])

    await update.message.reply_text(
        "👑 SaaS Platform Ready",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ================= HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    # ===== INPUTS =====
    if text == "➕ توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن")
        return

    if text == "🌐 API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API")
        return

    if text == "🌍 دولة":
        context.user_data["step"] = "country"
        await update.message.reply_text("📩 أرسل الدولة")
        return

    # ===== SAVE =====
    if step == "token":
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (text, user_id))
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

    # ===== RUN SYSTEM =====
    if text == "▶ تشغيل":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 النظام يعمل")

    if text == "⏹ إيقاف":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم الإيقاف")

    if text == "💎 اشتراك":
        cursor.execute("SELECT subscription FROM users WHERE user_id=?", (user_id,))
        sub = cursor.fetchone()[0]

        await update.message.reply_text(f"💎 اشتراكك: {sub}")

    # ===== ENGINE RESPONSE =====
    response = run_user_logic(user_id, text)
    await update.message.reply_text(response)


# ================= RUN =================
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 SaaS PRO Running")
app.run_polling()
