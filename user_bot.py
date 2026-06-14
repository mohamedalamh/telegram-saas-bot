from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import database as db
from durian_api import DurianAPI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

COUNTRY_MAP = {
    "679": {"name": "فيجي", "emoji": "🇫🇯"},
    "36": {"name": "هنغاريا", "emoji": "🇭🇺"},
    "373": {"name": "مولدوفا", "emoji": "🇲🇩"},
    # أضف أي دول أخرى هنا بنفس الصيغة
}
# القائمة الكاملة لجميع دول العالم ورموزها المتوافقة مع الـ API
ALL_COUNTRIES = [
    {"name": "روسيا 🇷🇺", "code": "ru"}, {"name": "أمريكا 🇺🇸", "code": "us"},
    {"name": "إندونيسيا 🇮🇩", "code": "id"}, {"name": "مصر 🇪🇬", "code": "eg"},
    {"name": "بريطانيا 🇬🇧", "code": "uk"}, {"name": "الهند 🇮🇳", "code": "in"},
    {"name": "البرازيل 🇧🇷", "code": "br"}, {"name": "المغرب 🇲🇦", "code": "ma"},
    {"name": "الجزائر 🇩🇿", "code": "dz"}, {"name": "تونس 🇹🇳", "code": "tn"},
    {"name": "العراق 🇮🇶", "code": "iq"}, {"name": "الأردن 🇯🇴", "code": "jo"},
    {"name": "السعودية 🇸🇦", "code": "sa"}, {"name": "الإمارات 🇦🇪", "code": "ae"},
    {"name": "الكويت 🇰🇼", "code": "kw"}, {"name": "البحرين 🇧🇭", "code": "bh"},
    {"name": "عمان 🇴🇲", "code": "om"}, {"name": "قطر 🇶🇦", "code": "qa"},
    {"name": "اليمن 🇾🇪", "code": "ye"}, {"name": "فلسطين 🇵🇸", "code": "ps"},
    {"name": "لبنان 🇱🇧", "code": "lb"}, {"name": "سوريا 🇸🇾", "code": "sy"},
    {"name": "السودان 🇸🇩", "code": "sd"}, {"name": "ليبيا 🇱🇾", "code": "ly"},
    {"name": "تركيا 🇹🇷", "code": "tr"}, {"name": "ألمانيا 🇩🇪", "code": "de"},
    {"name": "فرنسا 🇫🇷", "code": "fr"}, {"name": "إسبانيا 🇪🇸", "code": "es"},
    {"name": "إيطاليا 🇮🇹", "code": "it"}, {"name": "كندا 🇨🇦", "code": "ca"},
    {"name": "أسترايا 🇦🇺", "code": "au"}, {"name": "الصين 🇨🇳", "code": "cn"},
    {"name": "اليابان 🇯🇵", "code": "jp"}, {"name": "كوريا 🇰🇷", "code": "kr"},
    {"name": "فيتنام 🇻🇳", "code": "vn"}, {"name": "تايلاند 🇹🇭", "code": "th"},
    {"name": "ماليزيا 🇲🇾", "code": "my"}, {"name": "الفلبين 🇵🇭", "code": "ph"},
    {"name": "باكستان 🇵🇰", "code": "pk"}, {"name": "أفغانستان 🇦🇫", "code": "af"},
    {"name": "إيران 🇮🇷", "code": "ir"}, {"name": "كولومبيا 🇨🇴", "code": "co"},
    {"name": "المكسيك 🇲🇽", "code": "mx"}, {"name": "الأرجنتين 🇦🇷", "code": "ar"},
    {"name": "بيرو 🇵🇪", "code": "pe"}, {"name": "فنزويلا 🇻🇪", "code": "ve"},
    {"name": "تشيلي 🇨🇱", "code": "cl"}, {"name": "أوكرانيا 🇺🇦", "code": "ua"},
    {"name": "بولندا 🇵🇱", "code": "pl"}, {"name": "رومانيا 🇷🇴", "code": "ro"},
    {"name": "هولندا 🇳🇱", "code": "nl"}, {"name": "بلجيكا 🇧🇪", "code": "be"},
    {"name": "السويد 🇸🇪", "code": "se"}, {"name": "النرويج 🇳🇴", "code": "no"},
    {"name": "البرتغال 🇵🇹", "code": "pt"}, {"name": "جنوب أفريقيا 🇿🇦", "code": "za"},
    {"name": "نيجيريا 🇳🇬", "code": "ng"}, {"name": "كينيا 🇰🇪", "code": "ke"},
    {"name": "غانا 🇬🇭", "code": "gh"}, {"name": "إثيوبيا 🇪🇹", "code": "et"},
    {"name": "موريتانيا 🇲🇷", "code": "mr"}, {"name": "أوزبكستان 🇺🇿", "code": "uz"},
    {"name": "كازاخستان 🇰🇿", "code": "kz"}, {"name": "قرغيزستان 🇰🇬", "code": "kg"},
    {"name": "طاجيكستان 🇹🇯", "code": "tj"}, {"name": "تركمانستان 🇹🇲", "code": "tm"},
    {"name": "أذربيجان 🇦🇿", "code": "az"}, {"name": "جورجيا 🇬🇪", "code": "ge"},
    {"name": "أرمينيا 🇦🇲", "code": "am"}, {"name": "النمسا 🇦🇹", "code": "at"},
    {"name": "سويسرا 🇨🇭", "code": "ch"}, {"name": "اليونان 🇬🇷", "code": "gr"},
    {"name": "بلغاريا 🇧🇬", "code": "bg"}, {"name": "كرواتيا 🇭🇷", "code": "hr"},
    {"name": "صربيا 🇷🇸", "code": "rs"}, {"name": "جمهورية التشيك 🇨🇿", "code": "cz"},
    {"name": "المجر 🇭🇺", "code": "hu"}, {"name": "الدانمارك 🇩🇰", "code": "dk"},
    {"name": "فنلندا 🇫🇮", "code": "fi"}, {"name": "أيرلندا 🇮🇪", "code": "ie"},
    {"name": "نيوزيلندا 🇳🇿", "code": "nz"}, {"name": "سنغافورة 🇸🇬", "code": "sg"},
    {"name": "بغلاديش 🇧🇩", "code": "bd"}, {"name": "سريلانكا 🇱🇰", "code": "lk"},
    {"name": "نيبال 🇳🇵", "code": "np"}, {"name": "ميانمار 🇲🇲", "code": "mm"},
    {"name": "كمبوديا 🇰🇭", "code": "kh"}, {"name": "لاوس 🇱🇦", "code": "la"},
    {"name": "منغوليا 🇲🇳", "code": "mn"}, {"name": "أنغولا 🇦🇴", "code": "ao"},
    {"name": "الكاميرون 🇨🇲", "code": "cm"}, {"name": "ساحل العاج 🇨🇮", "code": "ci"},
    {"name": "السنغال 🇸🇳", "code": "sn"}, {"name": "زيمبابوي 🇿🇼", "code": "zw"},
    {"name": "تنزانيا 🇹🇿", "code": "tz"}, {"name": "أوغندا 🇺🇬", "code": "ug"},
    {"name": "زامبيا 🇿🇲", "code": "zm"}, {"name": "مدغشقر 🇲🇬", "code": "mg"},
    {"name": "كوبا 🇨🇺", "code": "cu"}, {"name": "بنما 🇵🇦", "code": "pa"},
    {"name": "كوستاريكا 🇨🇷", "code": "cr"}, {"name": "جامايكا 🇯🇲", "code": "jm"},
    {"name": "الأوروغواي 🇺🇾", "code": "uy"}, {"name": "الباراغواي 🇵🇾", "code": "py"},
    {"name": "بوليفيا 🇧🇴", "code": "bo"}, {"name": "الإكوادور 🇪🇨", "code": "ec"},
    {"name": "أيسلندا 🇮🇸", "code": "is"}, {"name": "قبرص 🇨🇾", "code": "cy"},
    {"name": "مالطا 🇲🇹", "code": "mt"}, {"name": "ألبانيا 🇦🇱", "code": "al"},
    {"name": "أندورا 🇦🇩", "code": "ad"}, {"name": "موناكو 🇲🇨", "code": "mc"},
    {"name": "سان مارينو 🇸🇲", "code": "sm"}, {"name": "جزر البهاما 🇧🇸", "code": "bs"},
    {"name": "باربادوس 🇧🇧", "code": "bb"}, {"name": "بليز 🇧🇿", "code": "bz"},
    {"name": "غويانا 🇬🇾", "code": "gy"}, {"name": "سورينام 🇸🇷", "code": "sr"},
    {"name": "فيجي 🇫يج", "code": "fj"}, {"name": "بابوا غينيا 🇵🇬", "code": "pg"},
    {"name": "جزر المالديف 🇲🇻", "code": "mv"}, {"name": "بروناي 🇧🇳", "code": "bn"},
    {"name": "بوتان 🇧🇹", "code": "bt"}
]

# ==================== 1. القائمة الرئيسية ====================
async def start_user_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔰 مرحباً بك في بوت صيد الأرقام 🔰\n\nاختر أحد الخيارات أدناه للبدء:"
    keyboard = [
        [InlineKeyboardButton("‹ ايقاف الصيد ›", callback_data="stop_hunting"), InlineKeyboardButton("‹ تشغيل الصيد ›", callback_data="start_hunting")],
        [InlineKeyboardButton("‹ إدارة الدول ›", callback_data="manage_countries"), InlineKeyboardButton("‹ اضافه دوله ›", callback_data="add_country_page_0")],
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
    
    if context.user_data.get("waiting_for_channel_id"):
        context.user_data.pop("waiting_for_channel_id", None)
        db.save_hunting_channel(user_id, text)
        
        keyboard = [[InlineKeyboardButton("⬅️ العودة للإعدادات", callback_data="bot_settings")]]
        await update.message.reply_text(
            f"✅ **تم ربط قناة الصيد بنجاح!**\n\n🆔 معرف القناة المسجل: `{text}`\n\n"
            f"⚠️ **ملاحظة هامة:** تأكد من رفع هذا البوت كـ **مشرف (Admin)** داخل القناة ومنحه صلاحية 'نشر الرسائل' لتتمكن المنصة من إنزال الأرقام فيها تلقائياً.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    elif context.user_data.get("waiting_for_username"):
        context.user_data["temp_username"] = text
        context.user_data.pop("waiting_for_username", None)
        context.user_data["waiting_for_apikey"] = True
        await update.message.reply_text("🔑 ممتاز، الآن قم بإرسال الـ **API Key** الخاص بك من إعدادات حسابك في الموقع:")
        return

    elif context.user_data.get("waiting_for_apikey"):
        username = context.user_data.get("temp_username")
        api_key = text
        context.user_data.pop("waiting_for_apikey", None)
        context.user_data.pop("temp_username", None)
        
        db.save_site_account(user_id, username, api_key)
        keyboard = [[InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="main_menu")]]
        await update.message.reply_text(
            f"✅ تم ربط حسابك بنجاح!\n\n👤 اسم المستخدم: `{username}`\n🔑 الـ API Key تم حفظه وتأمين مسار الصيد وجلب أرقام التليجرام.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

# ==================== 5. معالج الأحداث والأزرار الشامل ====================
async def user_bot_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if data == "main_menu":
        await start_user_bot(update, context)
        
    elif data == "bot_settings":
        await show_settings(update, user_id)
        
    elif data == "manage_accounts":
        await show_manage_accounts(update, user_id)
        
    elif data == "add_hunting_channel":
        context.user_data["waiting_for_channel_id"] = True
        await query.message.reply_text(
            "📥 **قم بإنشاء قناة عامة أو خاصة الآن، ثم اتبع الخطوات التالية:**\n\n"
            "1️⃣ قم إضافة هذا البوت كـ **مشرف (Admin)** داخل القناة.\n"
            "2️⃣ قم بنسخ **معرف القناة (Channel ID)** وإرساله هنا كرسالة نصية.\n\n"
            "💡 *نصيحة:* إذا كانت القناة عامة، أرسل الرابط المخفف كمعرف (مثل: `@MyHuntingChannel`). وإذا كانت خاصة، أرسل معرفها الرقمي الطويل المبتدئ بـ -100."
        )
        
    elif data == "add_new_site_account":
        context.user_data["waiting_for_username"] = True
        await query.message.reply_text("📥 فضلاً، أرسل الآن **اسم المستخدم (Username)** الخاص بحسابك في موقع DurianRCS:")
        
    elif data == "start_hunting":
        account = db.get_site_account(user_id)
        channel = db.get_hunting_channel(user_id)
        countries = db.get_user_countries(user_id)
        
        if not account:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى الانتقال إلى الإعدادات ➔ إدارة الحسابات وربط حسابك أولاً.")
            return
            
        if not channel:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى الانتقال إلى الإعدادات ➔ إضافة قناة الصيد وربط قناتك أولاً.")
            return

        if not countries:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى تفعيل دولة واحدة على الأقل من خيار ‹ اضافه دوله ›.")
            return
            
        username, api_key = account
        
        # التأكد من صحة الحساب وجلب نقاط الـ Score من الـ API الفعلي للموقع لقفل شروط التحقق
        balance = await DurianAPI.get_balance_by_name(username, api_key)
        
        # تفادي تشغيل مهام فحص مكررة لنفس المستخدم في الخلفية
        current_jobs = context.job_queue.get_jobs_by_name(f"hunt_{user_id}")
        if current_jobs:
            await query.message.reply_text("ℹ️ نظام الصيد والضخ لخدمة التليجرام يعمل بالفعل في قناتك الآن.")
            return

        # إطلاق مهمة الخلفية الدورية لتفحص الموقع وتسحب أرقام التليجرام كل 5 ثوانٍ تلقائياً
        context.job_queue.run_repeating(
            check_and_hunt_numbers, 
            interval=5, 
            first=1, 
            user_id=user_id, 
            name=f"hunt_{user_id}"
        )

        db.set_hunting_status(user_id, 1)
        await query.message.reply_text(
            f"🚀 **تم تفعيل وضع صيد أرقام التليجرام بنجاح!**\n\n"
            f"👤 الحساب النشط: `{username}`\n"
            f"💰 رصيدك في الموقع: `{balance} Score`\n"
            f"📢 قناة الصيد والضخ: `{channel}`\n\n"
            f"🔄 بدأ البوت بالفحص الدوري للموقع، وسيتم سحب وضخ أرقام التليجرام الحصرية في قناتك فور توفرها كل 5 ثوانٍ تلقائياً..."
        )
        
    elif data == "stop_hunting":
        db.set_hunting_status(user_id, 0)
        current_jobs = context.job_queue.get_jobs_by_name(f"hunt_{user_id}")
        if current_jobs:
            for job in current_jobs:
                job.schedule_removal()
        await query.message.reply_text("🛑 تم إيقاف عملية صيد وضخ أرقام التليجرام التلقائية بنجاح.")
        
    elif data.startswith("add_country_page_"):
        page = int(data.split("_")[-1])
        items_per_page = 8
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        
        page_countries = ALL_COUNTRIES[start_idx:end_idx]
        text = f"🗺️ **واجهة اختيار الدول - صفحة ({page + 1}):**\n\nاضغط على اسم الدولة لتفعيل الصيد منها مباشرة:"
        keyboard = []
        
        for i in range(0, len(page_countries), 2):
            row = []
            c1 = page_countries[i]
            row.append(InlineKeyboardButton(c1["name"], callback_data=f"save_c_{c1['name']}_{c1['code']}"))
            if i + 1 < len(page_countries):
                c2 = page_countries[i+1]
                row.append(InlineKeyboardButton(c2["name"], callback_data=f"save_c_{c2['name']}_{c2['code']}"))
            keyboard.append(row)
            
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ السابقة", callback_data=f"add_country_page_{page - 1}"))
        if end_idx < len(ALL_COUNTRIES):
            nav_row.append(InlineKeyboardButton("التالية ➡️", callback_data=f"add_country_page_{page + 1}"))
            
        if nav_row:
            keyboard.append(nav_row)
            
        keyboard.append([InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_menu")])
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("save_c_"):
        # استخراج اسم الدولة والرمز المكون من حرفين الممرر في الكولباك
        parts = data.split("_")
        country_name = parts[2]
        country_code = parts[3]
        
        # حفظ اسم الدولة أو رمزها المكون من حرفين في جدول PostgreSQL
        db.add_user_country(user_id, country_code) 
        await query.message.reply_text(f"🟢 تم إضافة وتفعيل دولة **{country_name}** بنجاح لتفعيل التليجرام!")
        await start_user_bot(update, context)

# ==================== 6. دالة الصيد والضخ التلقائي في الخلفية ====================
async def check_and_hunt_numbers(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.user_id
    
    account = db.get_site_account(user_id)
    channel = db.get_hunting_channel(user_id)
    countries = db.get_user_countries(user_id)
    
    if not account or not channel or not countries:
        job.schedule_removal()
        return

    username, api_key = account
    
    try:
        for country_code in countries:
            # طلب سحب الرقم باستخدام مشروعك الفعلي رقم "0257" وتفعيل الفحص التلقائي بالخلفية
            result = await DurianAPI.order_number_by_name(username, api_key, country_code, project_id="0257")
            
            if result and result.get("status") == "success":
                phone_number = result.get("number")
                number_status = result.get("number_status", "🔄 غير قادر على الفحص")
                
                # جلب معلومات الدولة من القاموس المعرف بالأعلى
                country_info = COUNTRY_MAP.get(str(country_code), {"name": f"كود {country_code}", "emoji": "🌐"})
                country_name = country_info["name"]
                country_emoji = country_info["emoji"]
                
                # صياغة نص الرسالة الاحترافي المتطابق مع الصورة
                message_text = (
                    f"🔰 <b>تم شراء رقم جديد من DurianRCS</b> 🔰\n\n"
                    f"- <b>الرقم :</b> <code>{phone_number}</code>\n"
                    f"- <b>الدولة :</b> {country_name} {country_emoji}\n"
                    f"- <b>الحالة :</b> {number_status}\n"
                    f"- <b>الكود :</b> ❗ قيد الإنتظار ❗"
                )
                
                # بناء الأزرار الشفافة المتطابقة مع لقطة الشاشة
                keyboard = [
                    [
                        InlineKeyboardButton("- طلب الكود .", callback_data=f"sms_{phone_number}"),
                        InlineKeyboardButton("- فك حظر .", callback_data=f"unban_{phone_number}")
                    ],
                    [
                        InlineKeyboardButton("- الغاء الرقم .", callback_data=f"cancel_{phone_number}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=channel, 
                    text=message_text, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup
                )
    except Exception as e:
        print(f"Error during hunting task for user {user_id}: {e}")

# ✅ حل الخطأ الثاني: تعديل دالة الاستقبال لحماية البوت من التوقف عند قراءة الرسائل الفارغة
async def handle_user_inputs(update: Update, context: CallbackContext):
    # تحقق حماية للتأكد من أن الحدث يحتوي على مستخدم حقيقي لتفادي خطأ NoneType
    if not update.effective_user:
        return
        
    user_id = update.effective_user.id
    # اكمل هنا بقية الكود الخاص بدالة handle_user_inputs الموجودة لديك في السطر 128 وما بعده...

def create_user_app(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_inputs))
    return app
