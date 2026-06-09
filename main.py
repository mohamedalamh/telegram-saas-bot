import os
import sqlite3
import threading
import uvicorn
from fastapi import FastAPI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# CONFIG
# =========================
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing in Railway Variables")

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
    status TEXT DEFAULT 'off'
)
""")
conn.commit()

# =========================
# FASTAPI WEB DASHBOARD
# =========================
web_app = FastAPI()

@web_app.get("/")
def home():
    cursor.execute("SELECT user_id, bot_token, api, country, status FROM users")
    users = cursor.fetchall()

    html = """
    <html>
    <head>
    <title>SaaS Dashboard</title>
    <style>
    body { font-family: Arial; background:#111; color:white; padding:20px }
    table { width:100%; border-collapse: collapse; }
    th, td { border:1px solid #444; padding:10px; text-align:center }
    th { background:#222 }
    </style>
    </head>
    <body>
    <h2>👑 SaaS Dashboard</h2>
    <table>
    <tr>
        <th>User ID</th>
        <th>Token</th>
        <th>API</th>
        <th>Country</th>
        <th>Status</th>
    </tr>
    """

    for u in users:
        html += f"""
        <tr>
            <td>{u[0]}</td>
            <td>{"✔" if u[1] else "❌"}</td>
            <td>{"✔" if u[2] else "❌"}</td>
            <td>{u[3]}</td>
            <td>{u[4]}</td>
        </tr>
        """

    html += "</table></body></html>"
    return html

# =========================
# START WEB SERVER
# =========================
def run_web():
    uvicorn.run(web_app, host="0.0.0.0", port=8000)

threading.Thread(target=run_web).start()

# =========================
# TELEGRAM BOT
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        ["🔑 إضافة توكن"],
        ["🌐 إضافة API"],
        ["🌍 الدولة"],
        ["▶ تشغيل"],
        ["⏹ إيقاف"],
        ["📊 الحالة"]
    ]

    await update.message.reply_text(
        "👋 أهلاً بك في نظام SaaS الاحترافي",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =========================
# HANDLER
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    step = context.user_data.get("step")

    if text == "🔑 إضافة توكن":
        context.user_data["step"] = "token"
        await update.message.reply_text("📩 أرسل التوكن")
        return

    if text == "🌐 إضافة API":
        context.user_data["step"] = "api"
        await update.message.reply_text("📩 أرسل API")
        return

    if text == "🌍 الدولة":
        context.user_data["step"] = "country"
        await update.message.reply_text("📩 أرسل الدولة")
        return

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

    if text == "▶ تشغيل":
        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🟢 تم التشغيل")
        return

    if text == "⏹ إيقاف":
        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("🔴 تم الإيقاف")
        return

    if text == "📊 الحالة":
        cursor.execute("SELECT bot_token, api, country, status FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()

        await update.message.reply_text(f"""
📊 الحالة:

🔑 Token: {"موجود" if data[0] else "غير موجود"}
🌐 API: {"موجود" if data[1] else "غير موجود"}
🌍 الدولة: {data[2]}
⚙ Status: {data[3]}
""")

# =========================
# RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app
