from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import database as db

# ==================== 1. القائمة الرئيسية ====================
async def start_user_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔰 مرحباً بك في بوت صيد الأرقام 🔰\n\nاختر أحد الخيارات أدناه للبدء:"
    keyboard = [
        [InlineKeyboardButton("‹ ايقاف الصيد ›", callback_data="stop_hunting"), InlineKeyboardButton("‹ تشغيل الصيد ›", callback_data="start_hunting")],
        [InlineKeyboardButton("‹ إدارة الدول ›", callback_data="manage_countries"), InlineKeyboardButton("‹ اضافه دوله ›", callback_data="add_country_page_1")],
        [InlineKeyboardButton("‹ اعدادات ›", callback_data="bot_settings")],
        [InlineKeyboardButton("‹ احصائيات عمليات الشراء الناجحه ›", callback_data="purchase_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

# ==================== 2. قائمة الإعدادات ====================
async def show_settings(update: Update):
    text = "⚙️ **قائمة الإعدادات:**\n\nقم بتعيين الإعدادات الأساسية للبوت قبل البدء في الصيد"
    keyboard = [
        [InlineKeyboardButton("‹ إضافة قناة الصيد ✅ ›", callback_data="add_hunting_channel")],
        [InlineKeyboardButton("‹ إدارة الحسابات ›", callback_data="manage_accounts")],
        [InlineKeyboardButton("‹ الباديات المرغوبة ›", callback_data="desired_prefixes")],
        [InlineKeyboardButton("‹ اللغة العربية 🌍 ›", callback_data="change_language")],
        [InlineKeyboardButton("‹ رجوع ›", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

# ==================== 3. إدارة الحسابات ====================
async def show_manage_accounts(update: Update, user_id: int):
    """عرض حساب الموقع المرتبط أو خيار إضافة حساب جديد"""
    account = db.get_site_account(user_id)
    
    if account:
        username, _ = account
        text = f"👤 **إدارة الحسابات:**\n\nحسابك الحالي المرتبط بموقع DurianRCS هو:\n👤 اسم المستخدم: `{username}`"
    else:
        text = "👤 **إدارة الحسابات:**\n\nلم تقم بربط أي حساب لموقع DurianRCS حتى الآن."

    keyboard = [
        [InlineKeyboardButton("➕ اضافه حساب جديد", callback_data="add_new_site_account")],
        [InlineKeyboardButton("‹ رجوع ›", callback_data="bot_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== 4. معالجة الإدخال النصي للحساب ====================
async def handle_user_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مستمع ذكي لاستقبال اسم المستخدم والـ API Key بشكل متسلسل"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # خطوة 1: استقبال اسم المستخدم والطلب الـ API Key
    if context.user_data.get("waiting_for_username"):
        context.user_data["temp_username"] = text
        context.user_data.pop("waiting_for_username", None)
        context.user_data["waiting_for_apikey"] = True
        await update.message.reply_text("🔑 ممتاز، الآن قم بإرسال الـ **API Key** الخاص بك من إعدادات حسابك في الموقع:")
        return

    # خطوة 2: استقبال الـ API Key والحفظ النهائي
    elif context.user_data.get("waiting_for_apikey"):
        username = context.user_data.get("temp_username")
        api_key = text
        
        context.user_data.pop("waiting_for_apikey", None)
        context.user_data.pop("temp_username", None)
        
        # حفظ البيانات في جدول الحسابات
        db.save_site_account(user_id, username, api_key)
        
        # إعادة توجيه المستخدم للواجهة الرئيسية للبوت الفرعي
        keyboard = [[InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="main_menu")]]
        await update.message.reply_text(
            f"✅ تم ربط حسابك بنجاح!\n\n👤 اسم المستخدم: `{username}`\n🔑 الـ API Key تم حفظه وتشفيره بنجاح لدورة الصيد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

# ==================== 5. معالج الأحداث والأزرار ====================
async def user_bot_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        await start_user_bot(update, context)
    elif query.data == "bot_settings":
        await show_settings(update)
    elif query.data == "manage_accounts":
        await show_manage_accounts(query, user_id)
        
    elif query.data == "add_new_site_account":
        context.user_data["waiting_for_username"] = True
        await query.message.reply_text("📥 فضلاً، أرسل الآن **اسم المستخدم (Username)** الخاص بحسابك في موقع DurianRCS:")
        
    elif query.data == "add_country_page_1":
        # إعادة تفعيل دالة الدول السابقة
        await query.message.reply_text("🗺️ واجهة الدول جاهزة.")

def create_user_app(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    # إضافة مستمع نصوص عام لاستقبال مدخلات اسم الحساب والـ API Key
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_inputs))
    return app
