import os
import multiprocessing
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import sqlite3

TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_token TEXT,
    status TEXT DEFAULT 'off'
)
""")
conn.commit()

# ====== تشغيل بوت مستخدم كـ Process ======
def run_bot(user_id, token):
    from telegram.ext import Application, CommandHandler

    app = Application.builder().token(token).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 بوتك يعمل الآن (SaaS Mode)")

    app.add_handler(CommandHandler("start", start))
    app.run_polling()

# ====== تخزين العمليات ======
processes = {}

# ====== Start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل /addtoken ثم التوكن الخاص بك"
    )

# ====== Message Handler ======
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text.startswith("/addtoken"):
        context.user_data["step"] = "token"
        await update.message.reply_text("أرسل التوكن")
        return

    if context.user_data.get("step") == "token":
        token = text

        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE users SET bot_token=? WHERE user_id=?", (token, user_id))
        conn.commit()

        context.user_data["step"] = None

        await update.message.reply_text("تم حفظ التوكن")
        return

    if text == "/startbot":
        cursor.execute("SELECT bot_token FROM users WHERE user_id=?", (user_id,))
        token = cursor.fetchone()[0]

        if user_id in processes:
            await update.message.reply_text("البوت شغال بالفعل")
            return

        p = multiprocessing.Process(target=run_bot, args=(user_id, token))
        p.start()

        processes[user_id] = p

        cursor.execute("UPDATE users SET status='on' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("تم تشغيل بوتك")
        return

    if text == "/stopbot":
        if user_id in processes:
            processes[user_id].terminate()
            del processes[user_id]

        cursor.execute("UPDATE users SET status='off' WHERE user_id=?", (user_id,))
        conn.commit()

        await update.message.reply_text("تم الإيقاف")
        return


app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CommandHandler("start", start))

print("Main SaaS Bot Running")
app.run_polling()
