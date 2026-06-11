import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import database as db
from bot_manager import bot_manager

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MAIN_TOKEN = os.getenv("MAIN_BOT_TOKEN")
# تحويل آمن لمعرف الأدمن لتفادي أخطاء القيمة الفارغة
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    ADMIN_ID = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    db_data = db.get_bot(user_id)
    # فحص الحظر بشكل آمن وصحيح
    if db_data and len(db_data) >= 4 and db_data[3] == 1:
        await update.message.reply_text("❌ عذراً، تم إيقاف حسابك وحظرك من استخدام المنصة من قبل الإدارة.")
        return

    await show_dashboard(update, user_id, user_name)

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text.strip()
    
    # التحقق إذا كان الأدمن يقوم بإدخال أوامر الإدارة النصية
    if user_id == ADMIN_ID and context.user_data.get("admin_action"):
        action = context.user_data.get("admin_action")
        try:
            target_id, value = text.split(" ")
            target_id = int(target_id)
            
            if action == "add_days":
                db.add_days_to_user(target_id, int(value))
                await update.message.reply_text(f"✅ تم إضافة {value} يوم للمستخدم `{target_id}` بنجاح.", parse_mode="Markdown")
            elif action == "ban":
                db.ban_user(target_id, int(value))
                status_text = "حظر" if value == "1" else "إلغاء حظر"
                await update.message.reply_text(f"✅ تم {status_text} المستخدم `{target_id}` بنجاح.", parse_mode="Markdown")
        except Exception:
            await update.message.reply_text("❌ صيغة خاطئة. يرجى الإدخال كالتالي: `المعرف القيمة` (مثال: 12345678 30)")
        
        context.user_data.pop("admin_action", None)
        return

    # معالجة التوكن الطبيعي للمستخدمين
    token = text
    status_msg = await update.message.reply_text("⏳ جاري التحقق من صحة التوكن المرسل...")
    is_valid = await bot_manager.validate_token(token)
    if not is_valid:
        await status_msg.edit_text("❌ التوكن غير صالح! تأكد من الحصول عليه بشكل صحيح من @BotFather.")
        return

    db.save_bot(user_id, token)
    await status_msg.delete() 
    await update.message.reply_text("✅ تم ربط وحفظ توكن البوت الخاص بك بنجاح!")
    await show_dashboard(update, user_id, user_name)

async def show_dashboard(update: Update, user_id: int, user_name: str):
    db_data = db.get_bot(user_id)
    
    days_left = "30 يوم"
    if db_data:
        status = bot_manager.get_status(user_id)
        # حساب الوقت المتبقي الفعلي بشكل آمن من تاريخ انتهاء الاشتراك
        if db_data[2]:
            try:
                # التحقق من نوع البيانات المسترجعة والتعامل معها كـ datetime
                expires_at = db_data[2]
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.split(".")[0])
                delta = expires_at - datetime.utcnow()
                days_left = f"{max(0, delta.days)} يوم"
            except Exception:
                days_left = "30 يوم"
    else:
        status = "⚪️ غير مربوط"
        
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
    
    if user_id == ADMIN_ID:
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
    if update.effective_user.id != ADMIN_ID:
        return
    await show_admin_panel(update)

async def show_admin_panel(update: Update):
    try:
        total, active = db.get_stats()
        total_val = total[0] if total else 0
        active_val = active[0] if active else 0
    except Exception:
        total_val, active_val = 0, 0

    text = (
        f"👑 **مرحباً بك في لوحة تحكم المطور الفنية** 👑\n\n"
        f"📊 إحصائيات المنصة الحالية:\n"
        f"👥 إجمالي البوتات المسجلة: {total_val}\n"
        f"🚀 البوتات النشطة حالياً: {active_val}\n\n"
        f"قم باختيار الإجراء المطلوب من الأزرار أدناه:"
    )
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
    db_data = db.get_bot(user_id)

    if query.data == "admin_panel" and user_id == ADMIN_ID:
        await show_admin_panel(update)
        return
    elif query.data == "adm_add_days" and user_id == ADMIN_ID:
        context.user_data["admin_action"] = "add_days"
        await query.message.reply_text("📥 أرسل الآن: (معرف المستخدم) ثم (فراغ) ثم (عدد الأيام).\nمثال: `12345678 30`")
        return
    elif query.data == "adm_ban" and user_id == ADMIN_ID:
        context.user_data["admin_action"] = "ban"
        await query.message.reply_text("📥 أرسل الآن: (معرف المستخدم) then (فراغ) then (1 للحظر أو 0 للإلغاء).\nمثال: `12345678 1`")
        return
    elif query.data == "main_menu":
        await show_dashboard(update, user_id, user_name)
        return

    if query.data == "show_token_info":
        if not db_data:
            await query.message.reply_text("📥 لم تقم بربط توكن حتى الآن.")
        else:
            await query.message.reply_text(f"🔑 توكنك المسجل الحالي هو:\n`{db_data[0]}`", parse_mode="Markdown")
            
    elif query.data == "run_bot":
        if not db_data:
            await query.message.reply_text("⚠️ يرجى إرسال توكن البوت أولاً لربطه بالمنصة:")
        else:
            success = await bot_manager.start_bot(user_id, db_data[0])
            if success:
                await query.message.reply_text("✅ تم تشغيل البوت بنجاح!")
            else:
                await query.message.reply_text("ℹ️ البوت يعمل بالفعل في الخلفية.")
            await show_dashboard(update, user_id, user_name)
            
    elif query.data == "stop_bot":
        if not db_data:
            await query.message.reply_text("❌ ليس لديك بوت نشط لإيقافه.")
        else:
            await bot_manager.stop_bot(user_id)
            await query.message.reply_text("🛑 تم إيقاف البوت بنجاح من السيرفر.")
            await show_dashboard(update, user_id, user_name)
        
    elif query.data == "renew_subscription":
        await query.message.reply_text("لتجديد اشتراكك، يرجى التواصل مع الإدارة مباشرة.")
        
    elif query.data == "contact_support":
        await query.message.reply_text("🤙 للدعم الفني تواصل مع المطور: @YourSupportUsername")
        
    elif query.data == "unban_bot":
        await query.message.reply_text("❗️ ميزة فك الحظر التلقائي قيد التطوير والصيانة حالياً.")

async def main():
    db.init_db()
    main_app = Application.builder().token(MAIN_TOKEN).build()
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(CommandHandler("admin", admin_command))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    main_app.add_handler(CallbackQueryHandler(button_handler))

    await main_app.initialize()
    await main_app.updater.start_polling()
    await main_app.start()
    await bot_manager.restore_active_bots()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await main_app.updater.stop()
        await main_app.stop()
        await main_app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
