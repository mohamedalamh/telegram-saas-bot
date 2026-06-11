from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== 1. القائمة الرئيسية ====================
async def start_user_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إظهار القائمة الرئيسية لبوت صيد الأرقام"""
    text = "🔰 مرحباً بك في بوت صيد الأرقام 🔰\n\nاختر أحد الخيارات أدناه للبدء:"
    
    keyboard = [
        [
            InlineKeyboardButton("‹ ايقاف الصيد ›", callback_data="stop_hunting"),
            InlineKeyboardButton("‹ تشغيل الصيد ›", callback_data="start_hunting")
        ],
        [
            InlineKeyboardButton("‹ إدارة الدول ›", callback_data="manage_countries"),
            InlineKeyboardButton("‹ اضافه دوله ›", callback_data="add_country_page_1")
        ],
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
    """إظهار قائمة الإعدادات الفرعية المطابقة للصورة"""
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

# ==================== 3. قائمة إضافة الدول (صفحة 1) ====================
async def show_countries_page_1(update: Update):
    """إظهار الصفحة الأولى من الدول المطابقة للصورة تماماً"""
    text = "🌍 **اختر الدولة المطلوبة:**\n\nيمكنك اختيار أكثر من دولة للصيد"
    
    keyboard = [
        [InlineKeyboardButton("قيرغيزستان 🇰🇬", callback_data="country_kg"), InlineKeyboardButton("روسيا 🇷🇺", callback_data="country_ru")],
        [InlineKeyboardButton("الولايات المتحدة 🇺🇸", callback_data="country_us"), InlineKeyboardButton("أوكرانيا 🇺🇦", callback_data="country_ua")],
        [InlineKeyboardButton("إسرائيل 🇮🇱", callback_data="country_il"), InlineKeyboardButton("كازاخستان 🇰🇿", callback_data="country_kz")],
        [InlineKeyboardButton("هونغ كونغ 🇭🇰", callback_data="country_hk"), InlineKeyboardButton("الصين 🇨🇳", callback_data="country_cn")],
        [InlineKeyboardButton("بولندا 🇵🇱", callback_data="country_pl"), InlineKeyboardButton("الفلبين 🇵🇭", callback_data="country_ph")],
        [InlineKeyboardButton("المملكة المتحدة 🇬🇧", callback_data="country_uk"), InlineKeyboardButton("ميانمار 🇲🇲", callback_data="country_mm")],
        [InlineKeyboardButton("مدغشقر 🇲🇬", callback_data="country_mg"), InlineKeyboardButton("إندونيسيا 🇮🇩", callback_data="country_id")],
        [InlineKeyboardButton("الكونغو 🇨🇩", callback_data="country_cd"), InlineKeyboardButton("ماليزيا 🇲🇾", callback_data="country_my")],
        [InlineKeyboardButton("نيجيريا 🇳🇬", callback_data="country_ng"), InlineKeyboardButton("مارتينيك 🇲🇶", callback_data="country_mq")],
        [InlineKeyboardButton("ماكاو 🇲🇴", callback_data="country_mo"), InlineKeyboardButton("تنزانيا 🇹🇿", callback_data="country_tz")],
        [InlineKeyboardButton("مصر 🇪🇬", callback_data="country_eg"), InlineKeyboardButton("فيتنام 🇻🇳", callback_data="country_vn")],
        [InlineKeyboardButton("كوريا الجنوبية 🇰🇷", callback_data="country_kr")],
        [InlineKeyboardButton("‹ التالي ›", callback_data="add_country_page_2")],
        [InlineKeyboardButton("‹ رجوع ›", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

# ==================== 4. قائمة إضافة الدول (صفحة 2 لباقي دول العالم) ====================
async def show_countries_page_2(update: Update):
    """إظهار الصفحة الثانية لباقي دول العالم الإضافية حسب طلبك"""
    text = "🌍 **اختر الدولة المطلوبة (صفحة 2):**\n\nيمكنك اختيار المزيد من الدول للصيد"
    
    keyboard = [
        [InlineKeyboardButton("المملكة العربية السعودية 🇸🇦", callback_data="country_sa"), InlineKeyboardButton("الإمارات العربية المتحدة 🇦🇪", callback_data="country_ae")],
        [InlineKeyboardButton("العراق 🇮🇶", callback_data="country_iq"), InlineKeyboardButton("الأردن 🇯🇴", callback_data="country_jo")],
        [InlineKeyboardButton("المغرب 🇲🇦", callback_data="country_ma"), InlineKeyboardButton("الجزائر 🇩🇿", callback_data="country_dz")],
        [InlineKeyboardButton("تونس 🇹🇳", callback_data="country_tn"), InlineKeyboardButton("ليبيا 🇱🇾", callback_data="country_ly")],
        [InlineKeyboardButton("اليمن 🇾🇪", callback_data="country_ye"), InlineKeyboardButton("عمان 🇴🇲", callback_data="country_om")],
        [InlineKeyboardButton("الكويت 🇰🇼", callback_data="country_kw"), InlineKeyboardButton("قطر 🇶🇦", callback_data="country_qa")],
        [InlineKeyboardButton("البحرين 🇧🇭", callback_data="country_bh"), InlineKeyboardButton("لبنان 🇱🇧", callback_data="country_lb")],
        [InlineKeyboardButton("تركيا 🇹🇷", callback_data="country_tr"), InlineKeyboardButton("ألمانيا 🇩🇪", callback_data="country_de")],
        [InlineKeyboardButton("فرنسا 🇫🇷", callback_data="country_fr"), InlineKeyboardButton("كندا 🇨🇦", callback_data="country_ca")],
        [InlineKeyboardButton("‹ السابق ›", callback_data="add_country_page_1")],
        [InlineKeyboardButton("‹ رجوع ›", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

# ==================== 5. معالج الأحداث والضغط على الأزرار ====================
async def user_bot_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # التنقلات الرئيسية والفرعية
    if query.data == "main_menu":
        await start_user_bot(update, context)
        
    elif query.data == "bot_settings":
        await show_settings(update)
        
    elif query.data == "add_country_page_1":
        await show_countries_page_1(update)
        
    elif query.data == "add_country_page_2":
        await show_countries_page_2(update)
        
    # إدارة عمليات التشغيل والإيقاف والإحصائيات
    elif query.data == "start_hunting":
        await query.message.reply_text("🚀 تم تفعيل وضع صيد الأرقام بنجاح وبدأ الفحص التلقائي...")
        
    elif query.data == "stop_hunting":
        await query.message.reply_text("🛑 تم إيقاف عمليات الصيد بشكل مؤقت.")
        
    elif query.data == "manage_countries":
        await query.message.reply_text("🗺️ واجهة إدارة الدول الحالية وتعديلها قيد التطوير الفني...")
        
    elif query.data == "purchase_stats":
        await query.message.reply_text("📊 إحصائيات عمليات الشراء الناجحة:\n\nعدد العمليات: 0 عملية حتى الآن.")
        
    # معالجة الضغط على أي دولة معينة (مثال تفاعلي)
    elif query.data.startswith("country_"):
        country_code = query.data.split("_")[1].upper()
        await query.message.reply_text(f"📍 تم تحديد واستهداف الدولة ذات الرمز ({country_code}) لبدء عملية الصيد عليها.")
        
    else:
        # معالجة بقية الأزرار الصامتة مؤقتاً
        await query.message.reply_text("ℹ️ هذا الخيار قيد التهيئة والربط مع السيرفر الفرعي.")

def create_user_app(token: str):
    """تجهيز وإقلاع تطبيق البوت الفرعي للمستخدم بشكل مستقل تماماً"""
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    
    return app
