import os
import sys
import sqlite3
import asyncio
import aiohttp
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# استلام التوكن من البوت الرئيسي
if len(sys.argv) > 2:
    BOT_ID = sys.argv[1]
    BOT_TOKEN = sys.argv[2]
else:
    print("❌ خطأ: يجب تشغيل البوت عبر البوت الرئيسي")
    sys.exit(1)

# ============ إعداد قاعدة البيانات ============
def init_db():
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_code TEXT UNIQUE,
        country_name TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS channel_settings (
        channel_id TEXT PRIMARY KEY,
        channel_username TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        api_key TEXT
    )''')
    conn.commit()
    conn.close()

# ============ دوال الدول ============
def get_countries():
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("SELECT country_code, country_name FROM countries")
    countries = c.fetchall()
    conn.close()
    return countries

def add_country(code, name):
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO countries (country_code, country_name) VALUES (?, ?)", (code.upper(), name))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def remove_country(code):
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("DELETE FROM countries WHERE country_code = ?", (code.upper(),))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# ============ دوال القناة ============
def get_channel():
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("SELECT channel_id, channel_username FROM channel_settings LIMIT 1")
    channel = c.fetchone()
    conn.close()
    return channel

def set_channel(channel_id):
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("DELETE FROM channel_settings")
    c.execute("INSERT INTO channel_settings (channel_id, channel_username) VALUES (?, ?)", (channel_id, channel_id))
    conn.commit()
    conn.close()

# ============ دوال الحسابات ============
def get_accounts():
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("SELECT username, api_key FROM accounts")
    accounts = c.fetchall()
    conn.close()
    return accounts

def add_account(username, api_key):
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO accounts (username, api_key) VALUES (?, ?)", (username, api_key))
    conn.commit()
    conn.close()

def remove_account(username):
    conn = sqlite3.connect(f'sub_bot_{BOT_ID}.db')
    c = conn.cursor()
    c.execute("DELETE FROM accounts WHERE username = ?", (username,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# ============ جلب الأرقام من API (مثال) ============
async def fetch_numbers(api_key, country_code):
    """هذه دالة مثال - قم بتعديلها حسب API الموقع الذي تستخدمه"""
    async with aiohttp.ClientSession() as session:
        try:
            # مثال: استبدل هذا الرابط برابط API الحقيقي
            url = "https://api.example.com/get-numbers"
            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"country": country_code, "limit": 5}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('numbers', [])
                else:
                    return []
        except Exception as e:
            print(f"خطأ: {e}")
            return []

# ============ إرسال الأرقام للقناة ============
async def send_numbers():
    channel = get_channel()
    if not channel:
        return
    
    channel_id = channel[0]
    countries = get_countries()
    accounts = get_accounts()
    
    if not countries or not accounts:
        return
    
    bot = application.bot
    
    for username, api_key in accounts:
        for code, name in countries:
            numbers = await fetch_numbers(api_key, code)
            for number in numbers:
                try:
                    await bot.send_message(chat_id=channel_id, text=f"📞 {number}\n🌍 {name}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"خطأ في الإرسال: {e}")

# ============ المهمة التلقائية ============
async def auto_fetch():
    while True:
        await send_numbers()
        await asyncio.sleep(300)  # كل 5 دقائق

# ============ أوامر البوت الفرعي ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌍 إدارة الدول", callback_data="countries")],
        [InlineKeyboardButton("📢 إعدادات القناة", callback_data="channel")],
        [InlineKeyboardButton("👥 إدارة الحسابات", callback_data="accounts")],
        [InlineKeyboardButton("🔄 بدء الجلب", callback_data="fetch_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎯 مرحباً! هذا البوت الفرعي {BOT_ID}\n\nاختر إعداداتك:",
        reply_markup=reply_markup
    )

async def countries_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    countries = get_countries()
    text = "🌍 الدول:\n\n"
    for code, name in countries:
        text += f"• {name} ({code})\n"
    text += "\nلإضافة دولة: /addcountry SA السعودية\nلحذف دولة: /removecountry SA"
    
    await query.edit_message_text(text)

async def add_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ استخدم: /addcountry SA السعودية")
        return
    
    code = context.args[0]
    name = ' '.join(context.args[1:])
    
    if add_country(code, name):
        await update.message.reply_text(f"✅ تم إضافة {name} ({code.upper()})")
    else:
        await update.message.reply_text(f"⚠️ الدولة {code} موجودة")

async def remove_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ استخدم: /removecountry SA")
        return
    
    code = context.args[0]
    if remove_country(code):
        await update.message.reply_text(f"✅ تم حذف الدولة {code.upper()}")
    else:
        await update.message.reply_text(f"⚠️ الدولة {code} غير موجودة")

async def channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    channel = get_channel()
    text = "📢 إعدادات القناة:\n\n"
    if channel:
        text += f"القناة الحالية: {channel[0]}\n"
    else:
        text += "لا توجد قناة محددة\n"
    text += "\nلتعيين قناة: /setchannel @username"
    
    await query.edit_message_text(text)

async def set_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ استخدم: /setchannel @username")
        return
    
    channel = context.args[0]
    set_channel(channel)
    await update.message.reply_text(f"✅ تم تعيين القناة {channel}")

async def accounts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    accounts = get_accounts()
    text = "👥 الحسابات:\n\n"
    for username, api_key in accounts:
        text += f"• {username}\n"
    text += "\nلإضافة حساب: /addaccount username api_key\nلحذف حساب: /removeaccount username"
    
    await query.edit_message_text(text)

async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ استخدم: /addaccount username api_key")
        return
    
    username = context.args[0]
    api_key = context.args[1]
    
    add_account(username, api_key)
    await update.message.reply_text(f"✅ تم إضافة حساب {username}")

async def remove_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ استخدم: /removeaccount username")
        return
    
    username = context.args[0]
    if remove_account(username):
        await update.message.reply_text(f"✅ تم حذف حساب {username}")
    else:
        await update.message.reply_text(f"⚠️ الحساب {username} غير موجود")

async def fetch_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🔄 جاري جلب الأرقام...")
    await send_numbers()
    await update.callback_query.edit_message_text("✅ تم جلب وإرسال الأرقام")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "countries":
        await countries_menu(update, context)
    elif data == "channel":
        await channel_menu(update, context)
    elif data == "accounts":
        await accounts_menu(update, context)
    elif data == "fetch_now":
        await fetch_now(update, context)

# ============ تشغيل البوت الفرعي ============
init_db()

application = Application.builder().token(BOT_TOKEN).build()

# أوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("addcountry", add_country_command))
application.add_handler(CommandHandler("removecountry", remove_country_command))
application.add_handler(CommandHandler("setchannel", set_channel_command))
application.add_handler(CommandHandler("addaccount", add_account_command))
application.add_handler(CommandHandler("removeaccount", remove_account_command))
application.add_handler(CallbackQueryHandler(handle_callback))

# بدء المهمة التلقائية
async def startup():
    asyncio.create_task(auto_fetch())

print(f"🚀 البوت الفرعي {BOT_ID} يعمل...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(startup())
    application.run_polling()
