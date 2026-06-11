from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import database as db
from durian_api import DurianAPI

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
async def show_settings(update: Update, user_id: int):
    """عرض قائمة الإعدادات مع تبيين حالة ربط القناة"""
    channel = db.get_hunting_channel(user_id)
    channel_status = f"✅ مربوطة ({channel})" if channel else "❌ غير مضافة"
    
    text = (
        f"⚙️ **قائمة الإعدادات:**\n\n"
        f"قناة الصيد الحالية: {channel_status}\n\n"
        f"قم بتعيين الإعدادات الأساسية للبوت قبل البدء في الصيد"
    )
    
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

# ==================== 4. معالجة الإدخالات النصية الشاملة ====================
async def handle_user_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # أ) استقبال وتخزين معرف قناة الصيد
    if context.user_data.get("waiting_for_channel_id"):
        context.user_data.pop("waiting_for_channel_id", None)
        
        # حفظ معرف القناة في قاعدة البيانات
        db.save_hunting_channel(user_id, text)
        
        keyboard = [[InlineKeyboardButton("⬅️ العودة للإعدادات", callback_data="bot_settings")]]
        await update.message.reply_text(
            f"✅ **تم ربط قناة الصيد بنجاح!**\n\n🆔 معرف القناة المسجل: `{text}`\n\n"
            f"⚠️ **ملاحظة هامة:** تأكد من رفع هذا البوت كـ **مشرف (Admin)** داخل القناة ومنحه صلاحية 'نشر الرسائل' (Post Messages) لتتمكن المنصة من إنزال الأرقام فيها تلقائياً.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # ب) استقبال اسم مستخدم موقع الأرقام
    elif context.user_data.get("waiting_for_username"):
        context.user_data["temp_username"] = text
        context.user_data.pop("waiting_for_username", None)
        context.user_data["waiting_for_apikey"] = True
        await update.message.reply_text("🔑 ممتاز، الآن قم بإرسال الـ **API Key** الخاص بك من إعدادات حسابك في الموقع:")
        return

    # ج) استقبال الـ API Key لموقع الأرقام
    elif context.user_data.get("waiting_for_apikey"):
        username = context.user_data.get("temp_username")
        api_key = text
        context.user_data.pop("waiting_for_apikey", None)
        context.user_data.pop("temp_username", None)
        
        db.save_site_account(user_id, username, api_key)
        
        keyboard = [[InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="main_menu")]]
        await update.message.reply_text(
            f"✅ تم ربط حسابك بنجاح!\n\n👤 اسم المستخدم: `{username}`\n🔑 الـ API Key تم حفظه وتأمين مسار الصيد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

# ==================== 5. معالج الأحداث والأزرار الشامل ====================
async def user_bot_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        await start_user_bot(update, context)
        
    elif query.data == "bot_settings":
        await show_settings(update, user_id)
        
    elif query.data == "manage_accounts":
        await show_manage_accounts(update, user_id)
        
    elif query.data == "add_hunting_channel":
        context.user_data["waiting_for_channel_id"] = True
        await query.message.reply_text(
            "📥 **قم بإنشاء قناة عامة أو خاصة الآن، ثم اتبع الخطوات التالية:**\n\n"
            "1️⃣ قم بإضافة هذا البوت كـ **مشرف (Admin)** داخل القناة.\n"
            "2️⃣ قم بنسخ **معرف القناة (Channel ID)** وإرساله هنا كرسالة نصية.\n\n"
            "💡 *نصيحة:* إذا كانت القناة عامة، أرسل الرابط المخفف كمعرف (مثل: `@MyHuntingChannel`). وإذا كانت خاصة، أرسل معرفها الرقمي الطويل المبتدئ بـ -100 (مثل: `-10021345678`)."
        )
        
    elif query.data == "add_new_site_account":
        context.user_data["waiting_for_username"] = True
        await query.message.reply_text("📥 فضلاً، أرسل الآن **اسم المستخدم (Username)** الخاص بحسابك في موقع DurianRCS:")
        
    elif query.data == "start_hunting":
        account = db.get_site_account(user_id)
        channel = db.get_hunting_channel(user_id)
        
        if not account:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى الانتقال إلى الإعدادات ➔ إدارة الحسابات وربط حسابك أولاً.")
            return
            
        if not channel:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى الانتقال إلى الإعدادات ➔ إضافة قناة الصيد وربط قناتك أولاً لتتمكن المنصة من إنزال الأرقام المقتنصة فيها.")
            return
            
        username, api_key = account
        balance = await DurianAPI.get_balance(api_key)
        
        if balance <= 0.0:
            await query.message.reply_text(f"⚠️ تم الاتصال بالحساب `{username}` بنجاح، ولكن رصيدك الحالي {balance}$، يرجى شحن الرصيد لبدء الصيد.")
            return

        context.user_data["is_hunting"] = True
        await query.message.reply_text(
            f"🚀 **تم تفعيل وضع الصيد التلقائي بنجاح!**\n\n"
            f"👤 الحساب النشط: `{username}`\n"
            f"💰 الرصيد الحالي: `{balance}$`\n"
            f"📢 قناة الصيد: `{channel}`\n\n"
            f"🔄 جاري الاتصال بالموقع لبدء سحب الأرقام وضخها في قناتك تلقائياً..."
        )
        
    elif query.data == "stop_hunting":
        context.user_data["is_hunting"] = False
        await query.message.reply_text("🛑 تم إيقاف عملية صيد الأرقام بشكل كامل.")
        
    elif query.data == "add_country_page_1":
        await query.message.reply_text("🗺️ واجهة الدول جاهزة ومستقرة.")

def create_user_app(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_inputs))
    return app
