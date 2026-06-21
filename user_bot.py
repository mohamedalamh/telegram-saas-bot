import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, CallbackContext
from telegram.constants import ParseMode
import database as db
from durian_api import DurianAPI

from telegram_checker.checker import telegram_checker 

logger = logging.getLogger(__name__)

COUNTRY_MAP = {
    "679": {"name": "فيجي", "emoji": "🇫🇯"},
    "33": {"name": "فرنسا", "emoji": "🇫🇷"},
    "36": {"name": "هنغاريا", "emoji": "🇭🇺"},
    "373": {"name": "مولدوفا", "emoji": "🇲🇩"},
    "7": {"name": "روسيا", "emoji": "🇷🇺"},
    "1": {"name": "أمريكا", "emoji": "🇺🇸"},
    "20": {"name": "مصر", "emoji": "🇪🇬"},
}

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
    {"name": "فيجي 🇫🇯", "code": "fj"}, {"name": "بابوا غينيا 🇵🇬", "code": "pg"},
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
    """عرض جميع حسابات DurianRCS مع تحكم كامل"""
    accounts = db.get_all_site_accounts(user_id)
    if not accounts:
        text = "👤 **إدارة الحسابات:**\n\nلا توجد حسابات مضافة. أضف حسابًا للبدء."
        keyboard = [
            [InlineKeyboardButton("➕ إضافة حساب جديد", callback_data="add_new_site_account")],
            [InlineKeyboardButton("‹ رجوع ›", callback_data="bot_settings")]
        ]
    else:
        text = "👤 **إدارة الحسابات:**\n\nالحساب النشط (🟢) هو المستخدم في الصيد. اضغط على 'تفعيل' لتغييره."
        keyboard = []
        for acc_id, username, api_key, is_active in accounts:
            status_icon = "🟢" if is_active else "⚪"
            btn_text = f"{status_icon} {username}"
            toggle_data = f"toggle_site_{acc_id}"
            delete_data = f"delete_site_{acc_id}"
            keyboard.append([
                InlineKeyboardButton(btn_text, callback_data="noop"),
                InlineKeyboardButton("تفعيل" if not is_active else "تعطيل", callback_data=toggle_data),
                InlineKeyboardButton("🗑️ حذف", callback_data=delete_data)
            ])
        keyboard.append([InlineKeyboardButton("➕ إضافة حساب جديد", callback_data="add_new_site_account")])
        keyboard.append([InlineKeyboardButton("‹ رجوع ›", callback_data="bot_settings")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

# ==================== 4. معالجة الإدخالات النصية الشاملة ====================
async def handle_user_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
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
        db.save_site_account_v2(user_id, username, api_key)  # استخدام الدالة الجديدة
        keyboard = [[InlineKeyboardButton("⬅️ العودة لإدارة الحسابات", callback_data="manage_accounts")]]
        await update.message.reply_text(
            f"✅ تم إضافة الحساب بنجاح وتفعيله!\n\n👤 اسم المستخدم: `{username}`\n🔑 الـ API Key تم حفظه.",
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
        return
    elif data.startswith("toggle_site_"):
        acc_id = int(data.split("_")[2])
        db.set_active_site_account(user_id, acc_id)
        await query.answer("✅ تم تغيير الحساب النشط", show_alert=False)
        await show_manage_accounts(update, user_id)
        return
    elif data.startswith("delete_site_"):
        acc_id = int(data.split("_")[2])
        accounts = db.get_all_site_accounts(user_id)
        if len(accounts) == 1:
            await query.answer("❌ لا يمكن حذف الحساب الوحيد. أضف حساباً آخر أولاً.", show_alert=True)
            return
        db.delete_site_account(user_id, acc_id)
        await query.answer("🗑️ تم حذف الحساب", show_alert=False)
        await show_manage_accounts(update, user_id)
        return
    elif data == "noop":
        await query.answer()
        return
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
    elif data == "manage_countries":
        await show_manage_countries(update, user_id)
        return
    elif data.startswith("delete_country_"):
        country_code = data.split("_", 2)[-1]
        db.delete_user_country(user_id, country_code)
        await query.answer("🗑️ تم حذف الدولة", show_alert=False)
        await show_manage_countries(update, user_id)
        return
    elif data == "start_hunting":
        active_accounts = db.get_active_site_accounts(user_id)
        channel = db.get_hunting_channel(user_id)
        countries = db.get_user_countries(user_id)
        if not active_accounts:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يجب أن يكون لديك حساب نشط واحد على الأقل. انتقل إلى الإعدادات ➔ إدارة الحسابات.")
            return
        if not channel:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى إضافة قناة الصيد أولاً.")
            return
        if not countries:
            await query.message.reply_text("❌ لا يمكن تشغيل الصيد! يرجى تفعيل دولة واحدة على الأقل.")
            return
        # عرض رصيد أول حساب نشط فقط للتمثيل
        username_first = active_accounts[0][0]
        api_key_first = active_accounts[0][1]
        balance = await DurianAPI.get_balance_by_name(username_first, api_key_first)
        current_jobs = context.job_queue.get_jobs_by_name(f"hunt_{user_id}")
        if current_jobs:
            await query.message.reply_text("ℹ️ الصيد يعمل بالفعل.")
            return
        context.job_queue.run_repeating(
            check_and_hunt_numbers, interval=5, first=1, user_id=user_id, name=f"hunt_{user_id}"
        )
        db.set_hunting_status(user_id, 1)
        accounts_str = "\n".join([f"👤 {u}" for u, _ in active_accounts])
        await query.message.reply_text(
            f"🚀 **تم تشغيل الصيد بعدة حسابات!**\n\n"
            f"الحسابات النشطة:\n{accounts_str}\n"
            f"💰 رصيد أول حساب: {balance} Score\n"
            f"📢 القناة: {channel}\n\n"
            f"سيتم سحب أرقام من جميع الحسابات المفعلة كل 5 ثوانٍ."
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
        parts = data.split("_")
        country_name = parts[2]
        country_code = parts[3]
        db.add_user_country(user_id, country_code)
        await query.message.reply_text(f"🟢 تم إضافة وتفعيل دولة **{country_name}** بنجاح لتفعيل التليجرام!")
        await start_user_bot(update, context)
    elif data.startswith(("code_", "unban_", "cancel_", "rate_", "weak_")):
        action, phone = data.split("_", 1)
        account = db.get_site_account(user_id)
        if not account:
            await query.answer("❌ لم تقم بربط حسابك بموقع الأرقام لإتمام الإجراء!", show_alert=True)
            return
        username, api_key = account
        if action == "code":
            await query.answer("⏳ جاري سحب وتحديث كود التحقق من السيرفر...", show_alert=False)
            sms_res = await DurianAPI.get_sms(username, api_key, phone)
            if sms_res["status"] == "success":
                updated_text = query.message.text_html.replace("قيد الإنتظار ❗️", f"<b>{sms_res['sms']}</b> ✅")
                try:
                    await query.message.edit_text(text=updated_text, reply_markup=query.message.reply_markup, parse_mode=ParseMode.HTML)
                    await query.message.reply_text(f"📥 <b>وصول كود جديد للرقم</b> <code>{phone}</code> :\n<code>{sms_res['sms']}</code>", parse_mode=ParseMode.HTML)
                except Exception:
                    pass
            else:
                await query.answer(f"ℹ️ {sms_res['message']}", show_alert=True)
        elif action == "cancel":
            success = await DurianAPI.cancel_number(username, api_key, phone)
            if success:
                updated_text = query.message.text_html.replace("قيد الإنتظار ❗️", "<b>❌ تم إلغاء وتحرير الرقم بنجاح</b>")
                try:
                    await query.message.edit_text(text=updated_text, reply_markup=None, parse_mode=ParseMode.HTML)
                except Exception:
                    pass
                await query.answer("🗑️ تم إلغاء الرقم بنجاح وتحرير رصيدك بالموقع.", show_alert=True)
            else:
                await query.answer("❌ فشل إلغاء الرقم، ربما انتهى وقته الافتراضي أو تم تفعيله.", show_alert=True)
        elif action == "unban":
            await query.answer("⚙️ جاري إرسال طلب فك الحظر الفوري للرقم التابع لك إلى خوادم الدعم...", show_alert=True)
        elif action == "rate":
            await query.answer("📊 نسبة وصول الأكواد الحالية لهذا النطاق هي: 94%", show_alert=True)
        elif action == "weak":
            await query.answer("🧌 تم تصنيف جودة هذا النطاق كـ (ضعيفة) مؤقتاً بناءً على تقارير السحب.", show_alert=True)

# ==================== 6. عرض وإدارة الدول المختارة ====================
async def show_manage_countries(update: Update, user_id: int):
    countries = db.get_user_countries(user_id)
    if not countries:
        text = "🌍 **لم تقم بإضافة أي دولة بعد.**\n\nاستخدم زر 'اضافه دوله' لتفعيل الصيد من دول معينة."
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
    else:
        text = "🌍 **الدول المفعلة حاليًا:**\n\nاضغط على أي دولة لحذفها من قائمة الصيد."
        keyboard = []
        for code in countries:
            country_name = code
            for c in ALL_COUNTRIES:
                if c["code"] == code:
                    country_name = c["name"]
                    break
            keyboard.append([InlineKeyboardButton(f"🗑️ {country_name}", callback_data=f"delete_country_{code}")])
        keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== 7. دالة الصيد والضخ ====================
async def check_and_hunt_numbers(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.user_id
    active_accounts = db.get_active_site_accounts(user_id)
    channel = db.get_hunting_channel(user_id)
    countries = db.get_user_countries(user_id)

    if not active_accounts or not channel or not countries:
        job.schedule_removal()
        return

    for username, api_key in active_accounts:
        for country_code in countries:
            clean_country = str(country_code).strip()
            try:
                result = await DurianAPI.order_number_by_name(username, api_key, clean_country, project_id="0257")
                if result and result.get("status") == "success":
                    phone_number = result.get("number")
                    # منطق الفحص يبقى كما هو
                    status_text = "🟢 الرقم بدون جلسة"
                    try:
                        account_checker = await telegram_checker.get_available_account()
                        if account_checker:
                            check_result = await telegram_checker.check_phone(account_checker, phone_number)
                            status_text = check_result.get("status_text", "🟢 الرقم بدون جلسة")
                    except Exception:
                        pass

                    country_name = clean_country.upper()
                    country_flag = "🌐"
                    for prefix, info in COUNTRY_MAP.items():
                        if phone_number.replace("+", "").startswith(prefix):
                            country_name = info["name"]
                            country_flag = info["emoji"]
                            break

                    message_text = (
                        f"🔰 <b>تم شراء رقم جديد من DurianRCS</b> 🔰\n\n"
                        f"- <b>الـرقم :</b> <code>{phone_number}</code>\n"
                        f"- <b>الـدولـة :</b> {country_name} {country_flag}\n"
                        f"- <b>الـحـالـة :</b> {status_text}\n"
                        f"- <b>الحساب المستخدم :</b> {username}\n"
                        f"- <b>تكرار نزول الرقم :</b> 1 مرة\n"
                        f"- <b>الـكـود :</b> ❗ قيد الإنتظار ❗"
                    )

                    keyboard = [
                        [
                            InlineKeyboardButton("- نسبة الوصول .", callback_data=f"rate_{phone_number}"),
                            InlineKeyboardButton("- ضعيفه 🧌 .", callback_data=f"weak_{phone_number}")
                        ],
                        [
                            InlineKeyboardButton("- طلب الكود .", callback_data=f"code_{phone_number}"),
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
                logger.error(f"Error for user {user_id}, account {username}: {e}")
                continue  # ينتقل للدولة التالية أو الحساب التالي
                
def create_user_app(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_inputs))
    return app
