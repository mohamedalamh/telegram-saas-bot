import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    api TEXT,
    country TEXT,
    status TEXT DEFAULT 'inactive',
    subscription TEXT DEFAULT 'free'
)
""")
conn.commit()

ADMIN_ID = 123456789  # 🔴 غيري هذا إلى رقم حسابك في Telegram

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["🔑 إضافة توكن البوت"],
        ["🌐 إضافة API"],
        ["🌍 اختيار الدولة"],
        ["▶ تشغيل البوت", "⏹ إيقاف البوت"],
        ["💎 الاشتراك"]
    ]

    # إذا أنتِ الأدمن
    if user_id == ADMIN_ID:
        keyboard.append(["⚙ لوحة الإدارة"])

    await update.message.reply_text(
        "👋 أهلاً بك في نظام SaaS",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =========================
# HANDLER
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    step = context.user_data.get("step")

    # ===== إدخال توكن =====
    if text == "🔑 إضافة توكن البوت":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن الآن")
        return

    # ===== إدخال API =====
    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API الآن")
        return

    # ===== اختيار الدولة =====
    if text == "🌍 اختيار الدولة":
        context.user_data["step"] = "country"
        await update.message.reply_text("📩 أرسل اسم الدولة")
        return

    # ===== استقبال البيانات =====
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

    # ===== تشغيل =====
    if text == "▶ تشغيل البوت":
        cursor.execute("UPDATE users SET status='active' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم التشغيل")
        return

    # ===== إيقاف =====
    if text == "⏹ إيقاف البوت":
        cursor.execute("UPDATE users SET status='inactive' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم الإيقاف")
        return

    # ===== الاشتراك =====
    if text == "💎 الاشتراك":
        cursor.execute("SELECT subscription FROM users WHERE user_id=?", (user_id,))
        sub = cursor.fetchone()[0]

        await update.message.reply_text(f"💎 اشتراكك: {sub}")
        return

    # ===== لوحة الأدمن =====
    if text == "⚙ لوحة الإدارة" and user_id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        await update.message.reply_text(f"""
⚙ لوحة الإدارة:

👥 عدد المستخدمين: {count}
        """)
        return

# =========================
# BOT RUN
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 SaaS System Running")
app.run_polling()
