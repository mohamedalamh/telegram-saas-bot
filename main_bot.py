import os
import asyncio
import logging
import sqlite3
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.request import HTTPXRequest # تم استيراده لمعالجة انتهاء مهلة الاتصال Timeout
import database as db
from bot_manager import bot_manager
from telegram_checker.login_manager import login_manager # استيراد مدير تسجيل الدخول

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_TOKEN = os.getenv("MAIN_BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except Exception:
    ADMIN_ID = 0

# تحديد مراحل المحادثة الخاصة بربط الحساب الفاحص من الهاتف
PHONE, CODE, PASSWORD = range(3)

def get_correct_table_name():
    """دالة ذكية لاكتشاف اسم الجدول الصحيح في قاعدة البيانات تلقائياً"""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        for t in tables:
            name = t[0]
            if name in ["bots", "users", "sub_bots", "telegram_bots", "bot_users"]:
                return name
        if tables:
            return tables[0][0]
    except Exception:
        pass
    return "bots"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    db_data = db.get_bot(user_id)
    if db_data and len(db_data) >= 4:
        if db_data[3] == 1:
            await update.message.reply_text("❌ عذراً، تم إيقاف حسابك وحظرك من استخدام المنصة من قبل الإدارة.")
            return
    await show_dashboard(update, user_id, user_name)

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text.strip()
    
    # التحقق مما إذا كان المدخل نصاً موجهاً للإدارة
    if ADMIN_ID != 0 and user_id == ADMIN_ID and context.user_data.get("admin_action"):
        action = context.user_data.get("admin_action")
        table_name = get_correct_table_name()
        
        if action == "add_days":
            try:
                target_id, value = text.split(" ")
                target_id = int(target_id)
                db.add_days_to_user(target_id, int(value))
                await update.message.reply_text(f"✅ تم إضافة {value} يوم للمستخدم `{target_id}` بنجاح.")
            except Exception:
                await update.message.reply_text("❌ صيغة خاطئة. يرجى إدخال: `المعرف القيمة` (مثال: `834033986 30`)")
            context.user_data.pop("admin_action", None)
            return
            
        elif action == "ban":
            try:
                target_id, value = text.split(" ")
                target_id = int(target_id)
                db.ban_user(target_id, int(value))
                status_text = "حظر" if int(value) == 1 else "إلغاء حظر"
                await update.message.reply_text(f"✅ تم تعديل حالة المستخدم `{target_id}` إلى: **{status_text}**.")
            except Exception:
                await update.message.reply_text("❌ صيغة خاطئة. يرجى إدخال: `المعرف القيمة` (مثال للحظر: `834033986 1`)")
            context.user_data.pop("admin_action", None)
            return
            
        elif action == "delete_user":
            try:
                target_id = int(text)
                try:
                    await bot_manager.stop_bot(target_id)
                except Exception:
                    pass
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (target_id,))
                conn.commit()
                conn.close()
                await update.message.reply_text(f"🗑️ تم حذف المستخدم `{target_id}` نهائياً من الجدول `{table_name}` وإيقاف خط السحب الخاص به.")
            except Exception as e:
                await update.message.reply_text(f"❌ فشل تنفيذ الحذف. الخطأ: {e}")
            context.user_data.pop("admin_action", None)
            return

    # معالجة استقبال التوكن الجديد وحفظه للمستخدم العادي بشكل طبيعي
    status_msg = await update.message.reply_text("⏳ جاري التحقق من صحة التوكن المرسل وحفظه...")
    is_valid = await bot_manager.validate_token(text)
    if not is_valid:
        await status_msg.edit_text("❌ التوكن غير صالح! تأكد من الحصول عليه بشكل صحيح من @BotFather.")
        return
    try:
        db.save_bot(user_id, text)
        await status_msg.delete()
        await update.message.reply_text("✅ تم شحن وتحديث توكن البوت الجديد بنجاح!")
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ في قاعدة البيانات: {e}")
        return
    await show_dashboard(update, user_id, user_name)

async def show_dashboard(update: Update, user_id: int, user_name: str):
    days_left = "36 يوم"
    status = "⚪️ غير مربوط"
    try:
        db_data = db.get_bot(user_id)
        if db_data and len(db_data) >= 4:
            status = bot_manager.get_status(user_id)
            expires_at = db_data[2]
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", ""))
                delta = expires_at.replace(tzinfo=None) - datetime.now(timezone.utc).replace(tzinfo=None)
                days_left = f"{max(0, delta.days)} يوم"
    except Exception:
        days_left = "36 يوم"
        
    text = (
        f"👤 ⪪ حياك الله يا {user_name} 🦾، أهلاً وسهلاً ومرحباً بك.\n\n"
        f"🟢 ⪪ لديك اشتراك نشط، يمكنك هنا تشغيل وإيقاف البوت الخاص بك ⪪ {status}\n\n"
        f"⏰ ⪪ اشتراكك ⪪ {days_left} ⪪"
    )
    keyboard = [
        [InlineKeyboardButton("🔑 توكن البوت", callback_data="show_token_info")],
        [
            InlineKeyboardButton("إيقاف البوت ❌", callback_data="stop_bot"),
            InlineKeyboardButton("تشغيل البوت ✅", callback_data="run_bot")
        ],
        [InlineKeyboardButton("🔄 تجديد الإشتراك", callback_data="renew_subscription")],
        [
            InlineKeyboardButton("تواصل مع الدعم 🤙", callback_data="contact_support"),
            InlineKeyboardButton("بوت فك الحظر ❗️", callback_data="unban_bot")
        ]
    ]
    if ADMIN_ID != 0 and user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("👑 لوحة تحكم الإدارة 👑", callback_data="admin_panel")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        except Exception:
            pass

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID == 0 or update.effective_user.id != ADMIN_ID:
        return
    await show_admin_panel(update)

async def show_admin_panel(update: Update):
    try:
        total, active = db.get_stats()
    except Exception:
        total, active = 0, 0
    text = (
        f"👑 **لوحة تحكم المطور الفنية الشاملة** 👑\n\n"
        f"📊 **إحصائيات النظام الفورية:**\n"
        f"👥 إجمالي المستخدمين في النظام: {total}\n"
        f"🚀 البوتات الفرعية النشطة حالياً: {active}\n\n"
        f"⚙️ قم باختيار الإجراء المناسب لإدارة المشتركين والاشتراكات الشهرية:"
    )
    keyboard = [
        [
            InlineKeyboardButton("➕ شحن/تجديد الأيام", callback_data="adm_add_days"),
            InlineKeyboardButton("🚫 حظر / إلغاء حظر", callback_data="adm_ban")
        ],
        [
            InlineKeyboardButton("🗑️ حذف مستخدم نهائياً", callback_data="adm_delete_user"),
            InlineKeyboardButton("🆔 استخراج الـ IDs", callback_data="adm_get_ids")
        ],
        [
            InlineKeyboardButton("⚙️ إضافة حساب فاحص", callback_data="adm_add_checker"),
            InlineKeyboardButton("⬅️ الواجهة الرئيسية", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

# دالات استقبال وإعداد ربط الحساب الفاحص من شات البوت (تدار من الهاتف)
async def start_add_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    
    if ADMIN_ID == 0 or user_id != ADMIN_ID:
        return ConversationHandler.END
        
    msg_text = (
        "🚀 **نظام ربط حساب الفحص التلقائي**\n\n"
        "أرسل بيانات الحساب الفاحص بالصيغة التالية تماماً:\n"
        "`الرقم,api_id,api_hash`\n\n"
        "مثال:\n"
        "`+967777777777,28412234,b3a6c98ea...`"
    )
    if query:
        await query.message.reply_text(msg_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg_text, parse_mode="Markdown")
    return PHONE

async def get_phone_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        phone, api_id, api_hash = text.split(",")
        context.user_data["chk_phone"] = phone.strip()
        context.user_data["chk_api_id"] = api_id.strip()
        context.user_data["chk_api_hash"] = api_hash.strip()
        
        await update.message.reply_text("⏳ جاري الاتصال بخوادم التليجرام وإرسال كود التحقق...")
        await login_manager.send_code(
            context.user_data["chk_phone"],
            context.user_data["chk_api_id"],
            context.user_data["chk_api_hash"]
        )
        await update.message.reply_text("💬 وصلك كود الآن على حساب التليجرام الفاحص، يرجى إرساله هنا فوراً:")
        return CODE
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الاتصال بالحساب أو أن الصيغة غير صحيحة.\nالخطأ: `{str(e)}` \n\nأرسل /add_checker للمحاولة مجدداً.")
        return ConversationHandler.END

async def get_code_and_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    phone = context.user_data["chk_phone"]
    await update.message.reply_text("⏳ جاري التحقق من كود تسجيل الدخول...")
    try:
        result = await login_manager.verify_code(phone, code)
        if result.get("status") == "PASSWORD_REQUIRED":
            await update.message.reply_text("🔒 هذا الحساب محمي بالتحقق بخطوتين، من فضلك أرسل باسوورد الحساب الآن:")
            return PASSWORD
        if result.get("status") == "SUCCESS":
            await update.message.reply_text(f"✅ تم ربط الحساب الفاحص بنجاح ممتد وضخه في قاعدة البيانات!\n👤 الاسم: {result.get('name')}")
            await login_manager.cleanup()
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ برميجي أثناء تفعيل الكود: `{str(e)}`")
        await login_manager.cleanup()
        return ConversationHandler.END

async def get_password_and_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    phone = context.user_data["chk_phone"]
    await update.message.reply_text("⏳ جاري فك التحقق بخطوتين وتخزين الجلسة...")
    try:
        result = await login_manager.verify_password(phone, password)
        if result.get("status") == "SUCCESS":
            await update.message.reply_text(f"✅ تم تخطي كلمة المرور بنجاح وحفظ الحساب الفاحص!\n👤 الاسم: {result.get('name')}")
    except Exception as e:
        await update.message.reply_text(f"❌ كلمة المرور خاطئة أو انتهت مهلة الجلسة: `{str(e)}`")
    finally:
        await login_manager.cleanup()
        return ConversationHandler.END

async def cancel_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await login_manager.cleanup()
    await update.message.reply_text("❌ تم إلغاء عملية ربط الحساب الفاحص بنجاح.")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    if ADMIN_ID != 0 and user_id == ADMIN_ID:
        if query.data == "admin_panel":
            await show_admin_panel(update)
            return
        elif query.data == "adm_add_days":
            context.user_data["admin_action"] = "add_days"
            await query.message.reply_text("📥 أرسل معرف المستخدم وعدد الأيام مفصولين بمسافة:\nمثال: `834033986 30`")
            return
        elif query.data == "adm_ban":
            context.user_data["admin_action"] = "ban"
            await query.message.reply_text("📥 أرسل معرف المستخدم وحالته مفصولين بمسافة:\n(`1` للحظر أو `0` لإلغاء الحظر)\nمثال: `834033986 1`")
            return
        elif query.data == "adm_delete_user":
            context.user_data["admin_action"] = "delete_user"
            await query.message.reply_text("🗑️ أرسل `ID المستخدم` المراد مسحه تماماً من السيرفر وإلغاء بوتاته:")
            return
        elif query.data == "adm_add_checker":
            # تفعيل المحادثة لربط الحساب الفاحص عند الضغط من لوحة التحكم
            await start_add_checker(update, context)
            return ConversationHandler.END
        elif query.data == "adm_get_ids":
            try:
                table_name = get_correct_table_name()
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                id_column = "user_id"
                if columns:
                    id_column = columns[0][1]
                cursor.execute(f"SELECT {id_column} FROM {table_name}")
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    user_list = "\n".join([f"👤 ID: `{row[0]}`" for row in rows])
                else:
                    user_list = "لا يوجد مستخدمين مسجلين حالياً."
                text = f"🆔 **قائمة معرّفات مستخدمي النظام التفصيلية:**\n*(تم القراءة من جدول: `{table_name}`)*\n\n{user_list}"
            except Exception as e:
                text = f"❌ تعذر استخراج المعرفات تلقائياً: {e}"
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="admin_panel")]]
            await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return
            
    if query.data == "main_menu":
        await show_dashboard(update, user_id, user_name)
        return
        
    db_data = db.get_bot(user_id)
    token = db_data[0] if (db_data and len(db_data) > 0) else None
    
    if query.data == "show_token_info":
        if not token:
            await query.message.reply_text("📥 لم تقم بربط توكن حتى الآن.")
        else:
            await query.message.reply_text(f"🔑 توكنك المسجل الحالي هو:\n`{token}`")
    elif query.data == "run_bot":
        if not token:
            await query.message.reply_text("⚠️ يرجى إرسال توكن البوت أولاً لربطه.")
        else:
            success = await bot_manager.start_bot(user_id, token)
            if success:
                await query.message.reply_text("✅ تم تشغيل البوت الفرعي بنجاح ممتد!")
            else:
                await query.message.reply_text("ℹ️ البوت الفرعي يعمل بالفعل في الخلفية.")
            await show_dashboard(update, user_id, user_name)
    elif query.data == "stop_bot":
        if not token:
            await query.message.reply_text("❌ ليس لديك بوت نشط لإيقافه.")
        else:
            await bot_manager.stop_bot(user_id)
            await query.message.reply_text("🛑 تم إيقاف البوت بنجاح.")
            await show_dashboard(update, user_id, user_name)
    elif query.data == "renew_subscription":
        await query.message.reply_text(
            f"⚙️ **لتجديد اشتراكك الشهري:**\n\n"
            f"يرجى التواصل مع الإدارة مباشرة وتزويدهم بالمعرف الخاص بك لتفعيل باقتك:\n"
            f"🆔 معرف حسابك: `{user_id}`", parse_mode="Markdown"
        )
    elif query.data in ["contact_support", "unban_bot"]:
        await query.message.reply_text("ℹ️ هذا الخيار قيد التهيئة الفنية حالياً.")

async def safe_restore():
    try:
        await bot_manager.restore_active_bots()
    except Exception as e:
        logger.error(f"Error restoring bots on startup: {e}")

async def main():
    try:
        db.init_db()
    except Exception as e:
        logger.error(f"Database init error: {e}")
        
    # ضبط مهلة طلبات الشبكة لتفادي انهيارات الـ ConnectTimeout الشائعة في التليجرام
    request_config = HTTPXRequest(connect_timeout=20.0, read_timeout=20.0)
    
    main_app = Application.builder().token(MAIN_TOKEN).request(request_config).build()
    
    # محادثة إضافة الحساب الفاحص لتفادي تداخل النصوص مع توكن البوت العادي
    checker_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add_checker", start_add_checker),
            CallbackQueryHandler(button_handler, pattern="^adm_add_checker$")
        ],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_and_send)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code_and_verify)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_and_verify)],
        },
        fallbacks=[CommandHandler("cancel", cancel_process)],
        per_message=False
    )
    
    main_app.add_handler(checker_conv)
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(CommandHandler("admin", admin_command))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    main_app.add_handler(CallbackQueryHandler(button_handler))
    
    await main_app.initialize()
    await main_app.updater.start_polling()
    await main_app.start()
    
    asyncio.create_task(safe_restore())
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await main_app.updater.stop()
        await main_app.stop()
        await main_app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
