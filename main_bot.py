import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import database as db
from bot_manager import bot_manager

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_TOKEN = os.getenv("MAIN_BOT_TOKEN")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except Exception:
    ADMIN_ID = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # فحص الحظر بشكل آمن من الحقل الرابع [token, is_active, expires_at, is_banned]
    db_data = db.get_bot(user_id)
    if db_data and len(db_data) >= 4:
        is_banned = db_data[3]
        if is_banned == 1:
            await update.message.reply_text("❌ عذراً، تم إيقاف حسابك وحظرك من استخدام المنصة من قبل الإدارة.")
            return

    await show_dashboard(update, user_id, user_name)

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text.strip()
    
    # أوامر الإدارة الخاصة بالأدمن
    if ADMIN_ID != 0 and user_id == ADMIN_ID and context.user_data.get("admin_action"):
        action = context.user_data.get("admin_action")
        try:
            target_id, value = text.split(" ")
            target_id = int(target_id)
            if action == "add_days":
                db.add_days_to_user(target_id, int(value))
                await update.message.reply_text(f"✅ تم إضافة {value} يوم للمستخدم `{target_id}`.")
            elif action == "ban":
                db.ban_user(target_id, int(value))
                await update.message.reply_text(f"✅ تم تعديل حالة حظر المستخدم `{target_id}`.")
        except Exception:
            await update.message.reply_text("❌ صيغة خاطئة. يرجى الإدخال: `المعرف القيمة`")
        context.user_data.pop("admin_action", None)
        return

    # استقبال توكن المستخدم العادي
    status_msg = await update.message.reply_text("⏳ جاري التحقق من صحة التوكن المرسل...")
    is_valid = await bot_manager.validate_token(text)
    if not is_valid:
        await status_msg.edit_text("❌ التوكن غير صالح! تأكد من الحصول عليه بشكل صحيح من @BotFather.")
        return

    try:
        db.save_bot(user_id, text)
        await status_msg.delete()
        await update.message.reply_text("✅ تم ربط وحفظ توكن البوت الخاص بك بنجاح!")
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ في قاعدة البيانات: {e}")
        return

    await show_dashboard(update, user_id, user_name)

async def show_dashboard(update: Update, user_id: int, user_name: str):
    days_left = "36 يوم, 3 ساعة"
    status = "⚪️ غير مربوط"
    
    try:
        db_data = db.get_bot(user_id)
        if db_data and len(db_data) >= 3:
            status = bot_manager.get_status(user_id)
            # استخراج تاريخ الانتهاء بأمان التام من الحقل الثالث
            expires_at = db_data[2]
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", ""))
                delta = expires_at.replace(tzinfo=None) - datetime.utcnow()
                days_left = f"{max(0, delta.days)} يوم"
    except Exception:
        days_left = "36 يوم, 3 ساعة"

    text = (
        f"👤 ⪪ حياك الله يا {user_name} 🦾، أهلاً وسهلاً ومرحباً بك.\n\n"
        f"🟢 ⪪ لديك اشتراك نشط، يمكنك هنا تشغيل وإيقاف البوت الخاص بك ⪪ {status}\n\n"
        f"⏰ ⪪ اشتراكك ⪪ {days_left} ⪪"
    )
    
    keyboard = [
        [InlineKeyboardButton("توكن البوت", callback_data="show_token_info")],
        [
            InlineKeyboardButton("إيقاف البوت ❌", callback_data="stop_bot"),
            InlineKeyboardButton("تشغيل البوت ✅", callback_data="run_bot")
        ],
        [InlineKeyboardButton("تجديد الإشتراك", callback_data="renew_subscription")],
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
    text = "👑 **مرحباً بك في لوحة تحكم المطور الفنية** 👑\n\nاختر الإجراء المطلوب:"
    keyboard = [
        [InlineKeyboardButton("➕ إضافة أيام لمستخدم", callback_data="adm_add_days")],
        [InlineKeyboardButton("🚫 حظر / إلغاء حظر مستخدم", callback_data="adm_ban")],
        [InlineKeyboardButton("⬅️ العودة للواجهة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

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
            await query.message.reply_text("📥 أرسل: (معرف المستخدم) (عدد الأيام)\nمثال: `12345678 30`")
            return
        elif query.data == "adm_ban":
            context.user_data["admin_action"] = "ban"
            await query.message.reply_text("📥 أرسل: (معرف المستخدم) (1 للحظر أو 0 للإلغاء)")
            return

    if query.data == "main_menu":
        await show_dashboard(update, user_id, user_name)
        return

    # تفكيك واستخراج التوكن الفعلي بشكل سليم [0] من مصفوفة قاعدة البيانات
    db_data = db.get_bot(user_id)
    token = db_data[0] if (db_data and len(db_data) > 0) else None

    if query.data == "show_token_info":
        if not token:
            await query.message.reply_text("📥 لم تقم بربط توكن حتى الآن.")
        else:
            await query.message.reply_text(f"🔑 توكنك الحالي هو:\n`{token}`")
            
    elif query.data == "run_bot":
        if not token:
            await query.message.reply_text("⚠️ يرجى إرسال توكن البوت أولاً لربطه.")
        else:
            success = await bot_manager.start_bot(user_id, token)
            if success:
                await query.message.reply_text("✅ تم تشغيل البوت بنجاح!")
            else:
                await query.message.reply_text("ℹ️ البوت يعمل بالفعل في الخلفية.")
            await show_dashboard(update, user_id, user_name)
            
    elif query.data == "stop_bot":
        if not token:
            await query.message.reply_text("❌ ليس لديك بوت نشط لإيقافه.")
        else:
            await bot_manager.stop_bot(user_id)
            await query.message.reply_text("🛑 تم إيقاف البوت بنجاح.")
            await show_dashboard(update, user_id, user_name)
        
    elif query.data in ["renew_subscription", "contact_support", "unban_bot"]:
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

    main_app = Application.builder().token(MAIN_TOKEN).build()
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
