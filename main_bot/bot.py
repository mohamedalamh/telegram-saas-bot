import os
import sqlite3
import asyncio
import subprocess
import sys
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============ إعداد قاعدة البيانات ============
def init_db():
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sub_bots (
        bot_id TEXT PRIMARY KEY,
        bot_token TEXT NOT NULL,
        owner_id INTEGER NOT NULL,
        owner_username TEXT,
        status TEXT DEFAULT 'stopped',
        subscription_end DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# ============ التوكن الخاص بالبوت الرئيسي ============
MAIN_BOT_TOKEN = "ضع_توكن_البوت_الرئيسي_هنا"
ADMIN_IDS = [123456789]  # ضع معرف التليجرام الخاص بك هنا

# قاموس لتخزين عمليات البوتات الفرعية
running_processes = {}

# ============ دوال مساعدة ============
def save_sub_bot(bot_id, bot_token, owner_id, owner_username):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    subscription_end = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    c.execute("INSERT OR REPLACE INTO sub_bots VALUES (?, ?, ?, ?, ?, ?, ?)",
              (bot_id, bot_token, owner_id, owner_username, 'stopped', subscription_end, datetime.now()))
    conn.commit()
    conn.close()

def get_user_bots(owner_id):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sub_bots WHERE owner_id = ?", (owner_id,))
    bots = c.fetchall()
    conn.close()
    return bots

def update_bot_status(bot_id, status):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    c.execute("UPDATE sub_bots SET status = ? WHERE bot_id = ?", (status, bot_id))
    conn.commit()
    conn.close()

def get_bot_token(bot_id):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    c.execute("SELECT bot_token FROM sub_bots WHERE bot_id = ?", (bot_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def check_subscription(bot_id):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    c.execute("SELECT subscription_end FROM sub_bots WHERE bot_id = ?", (bot_id,))
    result = c.fetchone()
    conn.close()
    if result:
        expiry_date = datetime.strptime(result[0], '%Y-%m-%d')
        return expiry_date > datetime.now()
    return False

def renew_subscription(bot_id):
    conn = sqlite3.connect('sub_bots.db')
    c = conn.cursor()
    new_expiry = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    c.execute("UPDATE sub_bots SET subscription_end = ? WHERE bot_id = ?", (new_expiry, bot_id))
    conn.commit()
    conn.close()

# ============ تشغيل وإيقاف البوتات الفرعية ============
async def start_sub_bot(bot_id, token):
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sub_bot', 'bot.py')
    process = await asyncio.create_subprocess_exec(
                sys.executable, script_path, bot_id, token,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
    running_processes[bot_id] = process
    update_bot_status(bot_id, 'running')

async def stop_sub_bot(bot_id):
    if bot_id in running_processes:
        running_processes[bot_id].terminate()
        await running_processes[bot_id].wait()
        del running_processes[bot_id]
    update_bot_status(bot_id, 'stopped')

# ============ أوامر البوت الرئيسي ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ إضافة بوت جديد", callback_data="add_bot")],
        [InlineKeyboardButton("📋 قائمة بوتاتي", callback_data="my_bots")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎉 مرحباً بك في نظام البوتات!\n\n"
        "يمكنك إضافة وإدارة البوتات الخاصة بك.\n"
        "استخدم الأزرار أدناه للبدء.",
        reply_markup=reply_markup
    )

async def add_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔑 أرسل توكن البوت الذي حصلت عليه من @BotFather\n\n"
        "مثال: 1234567890:ABCdefGHIjklm"
    )
    context.user_data['waiting_for_token'] = True

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_token'):
        token = update.message.text.strip()
        bot_id = token.split(':')[0] if ':' in token else token
        
        save_sub_bot(bot_id, token, update.effective_user.id, update.effective_user.username or "بدون اسم")
        
        await update.message.reply_text(
            f"✅ تم إضافة البوت بنجاح!\n\n"
            f"🆔 معرف البوت: {bot_id}\n"
            f"📅 الاشتراك: 30 يوم\n\n"
            f"استخدم /mybots لإدارة بوتاتك"
        )
        context.user_data['waiting_for_token'] = False

async def my_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bots = get_user_bots(update.effective_user.id)
    
    if not bots:
        await update.message.reply_text("📭 ليس لديك أي بوتات. استخدم /addbot لإضافة بوت!")
        return
    
    for bot in bots:
        bot_id, token, owner_id, owner_username, status, expiry, created = bot
        is_valid = check_subscription(bot_id)
        
        keyboard = []
        if status == 'running':
            keyboard.append([InlineKeyboardButton("⏹️ إيقاف", callback_data=f"stop_{bot_id}")])
        else:
            keyboard.append([InlineKeyboardButton("▶️ تشغيل", callback_data=f"start_{bot_id}")])
        
        keyboard.append([InlineKeyboardButton("🔄 تجديد", callback_data=f"renew_{bot_id}")])
        
        status_emoji = "🟢" if status == 'running' else "🔴"
        expiry_status = "✅ فعال" if is_valid else "❌ منتهي"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{status_emoji} البوت: {bot_id}\n"
            f"الحالة: {status}\n"
            f"الاشتراك: {expiry_status}\n"
            f"ينتهي في: {expiry}",
            reply_markup=reply_markup
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "add_bot":
        await add_bot_command(update, context)
        await query.message.delete()
    
    elif data == "my_bots":
        await my_bots(update, context)
        await query.message.delete()
    
    elif data.startswith("start_"):
        bot_id = data.replace("start_", "")
        token = get_bot_token(bot_id)
        if token and check_subscription(bot_id):
            await start_sub_bot(bot_id, token)
            await query.edit_message_text(f"✅ تم تشغيل البوت {bot_id}")
        elif not check_subscription(bot_id):
            await query.edit_message_text(f"❌ اشتراك البوت {bot_id} منتهي. جدد الاشتراك أولاً")
    
    elif data.startswith("stop_"):
        bot_id = data.replace("stop_", "")
        await stop_sub_bot(bot_id)
        await query.edit_message_text(f"⏹️ تم إيقاف البوت {bot_id}")
    
    elif data.startswith("renew_"):
        bot_id = data.replace("renew_", "")
        renew_subscription(bot_id)
        await query.edit_message_text(f"✅ تم تجديد اشتراك البوت {bot_id} لمدة 30 يوماً")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_token'] = False
    await update.message.reply_text("❌ تم الإلغاء")

# ============ تشغيل البوت ============
def main():
    init_db()
    
    application = Application.builder().token(MAIN_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addbot", add_bot_command))
    application.add_handler(CommandHandler("mybots", my_bots))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # معالجة التوكن
    application.add_handler(CommandHandler("cancel", cancel))
    
    print("🚀 البوت الرئيسي يعمل...")
    application.run_polling()

if __name__ == "__main__":
    main()
