import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import database as db
from bot_manager import bot_manager

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MAIN_TOKEN = os.getenv("MAIN_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    db_data = db.get_bot(user_id)
    
    if not db_data:
        # رسالة ترحيبية أولية إذا لم يكن مسجلاً
        await update.message.reply_text(
            f"👤 ⪪ حياك الله يا {user_name} 🦾، أهلاً وسهلاً ومرحباً بك.\n\n"
            "فصلاً، قم بإرسال توكن بوت تيليجرام الخاص بك من @BotFather للبدء والتحكم به مجاناً."
        )
    else:
        await show_dashboard(update, user_id, user_name)

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    token = update.message.text.strip()
    
    status_msg = await update.message.reply_text("⏳ جاري التحقق من صحة التوكن المرسل...")
    
    is_valid = await bot_manager.validate_token(token)
    if not is_valid:
        await status_msg.edit_text("❌ التوكن غير صالح! تأكد من الحصول عليه بشكل صحيح من @BotFather.")
        return

    db.save_bot(user_id, token)
    await status_msg.delete() # حذف رسالة الانتظار
    await show_dashboard(update, user_id, user_name)

async def show_dashboard(update: Update, user_id: int, user_name: str):
    # جلب حالة البوت الحالية من مدير النظام
    status = bot_manager.get_status(user_id)
    
    # تحضير النص المطابق تماماً للصورة المرسلة
    text = (
        f"👤 ⪪ حياك الله يا {user_name} 🦾، أهلاً وسهلاً ومرحباً بك.\n\n"
        f"🟢 ⪪ لديك اشتراك نشط، يمكنك هنا تشغيل وإيقاف البوت الخاص بك ⪪ {status}\n\n"
        f"⏰ ⪪ اشتراكك ⪪ 36 يوم, 3 ساعة ⪪"
    )
    
    # بناء لوحة الأزرار (نفس تقسيم وخانات الصورة تماماً)
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # التحقق إن كان الطلب من رسالة جديدة أو ضغطة زر لتحديث القائمة دون إرسال رسائل متكررة
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    db_data = db.get_bot(user_id)

    if not db_data:
        await query.message.reply_text("يرجى إرسال توكن البوت الخاص بك أولاً.")
        return

    token, _ = db_data

    if query.data == "run_bot":
        success = await bot_manager.start_bot(user_id, token)
        if success:
            await query.message.reply_text("✅ تم تشغيل البوت بنجاح!\nنوع البوت: DurianRCS (حسابين)\n\n⚠️ إذا كان بوتك DURIAN أو GRIZZLY ولم يتم تشغيل البوت انتظر 5 دقائق لا تقم بإيقافه.")
        else:
            await query.message.reply_text("ℹ️ البوت يعمل بالفعل في الخلفية أو معطل حالياً.")
            
    elif query.data == "stop_bot":
        success = await bot_manager.stop_bot(user_id)
        if success:
            await query.message.reply_text("🛑 تم إيقاف البوت بنجاح من السيرفر.")
        else:
            await query.message.reply_text("ℹ️ البوت متوقف بالفعل.")
            
    elif query.data == "show_token_info":
        await query.message.reply_text(f"🔑 توكنك المسجل الحالي هو:\n`{token}`", parse_mode="Markdown")
        
    elif query.data == "renew_subscription":
        await query.message.reply_text("لتجديد اشتراكك السنوي أو الشهري، يرجى التواصل مع الإدارة مباشرة.")
        
    elif query.data == "contact_support":
        await query.message.reply_text("🤙 للدعم الفني والاستفسارات تواصل مع المطور: @YourSupportUsername")
        
    elif query.data == "unban_bot":
        await query.message.reply_text("❗️ ميزة فك الحظر التلقائي قيد التطوير والصيانة حالياً.")

    # تحديث لوحة التحكم الرئيسية بعد أي إجراء لحفظ الحالة الجديدة
    await show_dashboard(update, user_id, user_name)

async def main():
    db.init_db()
    
    main_app = Application.builder().token(MAIN_TOKEN).build()
    main_app.add_handler(CommandHandler("start", start))
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
