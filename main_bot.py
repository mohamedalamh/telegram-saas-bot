import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import database as db
from bot_manager import bot_manager

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MAIN_TOKEN = os.getenv("MAIN_BOT_TOKEN", "YOUR_MAIN_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_data = db.get_bot(user_id)
    
    if not db_data:
        await update.message.reply_text("أهلاً بك في منصة SaaS للبوتات! فضلاً أرسل توكن بوت تيليجرام الخاص بك لربطه.")
    else:
        await show_dashboard(update, user_id)

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    token = update.message.text.strip()
    
    # رسالة انتظار للمستخدم
    status_msg = await update.message.reply_text("⏳ جاري التحقق من صحة التوكن...")
    
    is_valid = await bot_manager.validate_token(token)
    if not is_valid:
        await status_msg.edit_text("❌ التوكن غير صالح! تأكد من الحصول عليه بشكل صحيح من @BotFather.")
        return

    db.save_bot(user_id, token)
    await status_msg.edit_text("✅ تم التحقق من التوكن وحفظه بنجاح!")
    await show_dashboard(update, user_id)

async def show_dashboard(update: Update, user_id: int):
    status = bot_manager.get_status(user_id)
    keyboard = [
        [InlineKeyboardButton("▶️ تشغيل البوت", callback_data="run_bot"),
         InlineKeyboardButton("⏹️ إيقاف البوت", callback_data="stop_bot")],
        [InlineKeyboardButton("🔄 تحديث الحالة", callback_data="refresh_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"⚙️ **لوحة التحكم ببوتك الخاص:**\n\nالحالة الحالية: {status}"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_data = db.get_bot(user_id)

    if not db_data:
        await query.message.reply_text("لم يتم العثور على توكن مسجل. يرجى إرسال التوكن أولاً.")
        return

    token, _ = db_data

    if query.data == "run_bot":
        success = await bot_manager.start_bot(user_id, token)
        if success:
            await query.message.reply_text("🚀 تم تشغيل بوتك بنجاح وهو الآن مستعد لتلقي الأوامر!")
        else:
            await query.message.reply_text("ℹ️ البوت يعمل بالفعل أو حدث خطأ أثناء التشغيل.")
            
    elif query.data == "stop_bot":
        success = await bot_manager.stop_bot(user_id)
        if success:
            await query.message.reply_text("🛑 تم إيقاف بوتك بنجاح.")
        else:
            await query.message.reply_text("ℹ️ البوت متوقف بالفعل.")

    await show_dashboard(update, user_id)

async def main():
    db.init_db()
    
    # تشغيل البوت الرئيسي
    main_app = Application.builder().token(MAIN_TOKEN).build()
    main_app.add_handler(CommandHandler("start", start))
    main_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    main_app.add_handler(CallbackQueryHandler(button_handler))

    await main_app.initialize()
    await main_app.updater.start_polling()
    await main_app.start()

    # استعادة البوتات النشطة تلقائياً للمستخدمين عند الإقلاع
    await bot_manager.restore_active_bots()

    # الحفاظ على التطبيق قيد التشغيل المستمر
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await main_app.updater.stop()
        await main_app.stop()
        await main_app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
