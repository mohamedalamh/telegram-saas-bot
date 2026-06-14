from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import database as db
from durian_api import DurianAPI

# ==================== الدول (كما هي بدون حذف) ====================
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

# ==================== START ====================
async def start_user_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔰 مرحباً بك في بوت صيد الأرقام 🔰"
    keyboard = [
        [InlineKeyboardButton("تشغيل الصيد", callback_data="start_hunting")],
        [InlineKeyboardButton("إيقاف الصيد", callback_data="stop_hunting")],
        [InlineKeyboardButton("إدارة الدول", callback_data="add_country_page_0")],
        [InlineKeyboardButton("الإعدادات", callback_data="bot_settings")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== SETTINGS ====================
async def show_settings(update: Update, user_id: int):
    channel = db.get_hunting_channel(user_id)
    text = f"القناة: {channel if channel else 'غير مضافة'}"
    await update.callback_query.message.edit_text(text)

# ==================== CALLBACK ====================
async def user_bot_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # MAIN MENU
    if data == "main_menu":
        await start_user_bot(update, context)

    elif data == "bot_settings":
        await show_settings(update, user_id)

    elif data == "start_hunting":
        account = db.get_site_account(user_id)
        channel = db.get_hunting_channel(user_id)
        countries = db.get_user_countries(user_id)

        if not account or not channel or not countries:
            await query.message.reply_text("⚠️ أكمل الإعدادات أولاً")
            return

        username, api_key = account

        try:
            balance = await DurianAPI.get_balance_by_name(username, api_key)
        except:
            balance = 0

        context.job_queue.run_repeating(
            check_and_hunt_numbers,
            interval=5,
            first=1,
            user_id=user_id,
            name=f"hunt_{user_id}"
        )

        await query.message.reply_text("🚀 بدأ الصيد")

    elif data == "stop_hunting":
        jobs = context.job_queue.get_jobs_by_name(f"hunt_{user_id}")
        for j in jobs:
            j.schedule_removal()
        await query.message.reply_text("🛑 توقف الصيد")

    elif data.startswith("add_country_page_"):
        page = int(data.split("_")[-1])
        start = page * 8
        end = start + 8

        page_countries = ALL_COUNTRIES[start:end]
        keyboard = []

        for i in range(0, len(page_countries), 2):
            row = [InlineKeyboardButton(page_countries[i]["name"], callback_data=f"save_{page_countries[i]['code']}")]
            if i+1 < len(page_countries):
                row.append(InlineKeyboardButton(page_countries[i+1]["name"], callback_data=f"save_{page_countries[i+1]['code']}"))
            keyboard.append(row)

        await query.message.edit_text("اختر الدول", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("save_"):
        code = data.split("_")[1]
        db.add_user_country(user_id, code)
        await query.message.reply_text("تمت الإضافة")

# ==================== CHECK ====================
async def check_and_hunt_numbers(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.user_id

    account = db.get_site_account(user_id)
    channel = db.get_hunting_channel(user_id)
    countries = db.get_user_countries(user_id)

    if not account or not channel:
        job.schedule_removal()
        return

    username, api_key = account

    try:
        for c in countries:
            result = await DurianAPI.order_number_by_name(username, api_key, c, project_id="0257")

            if not result:
                continue

            phone = result.get("number")

            # ==================== NEW: PHONE CHECK ====================
            status = await check_phone(phone)

            if status == "banned":
                tag = "❌ محظور"
            elif status == "session":
                tag = "⚠️ لديه جلسة"
            else:
                tag = "✅ بدون جلسة"

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📩 طلب الكود", callback_data=f"code:{phone}"),
                    InlineKeyboardButton("❌ إلغاء", callback_data=f"cancel:{phone}")
                ]
            ])

            text = f"""
📞 رقم جديد

{phone}
الحالة: {tag}
"""

            await context.bot.send_message(chat_id=channel, text=text, reply_markup=keyboard)

    except Exception as e:
        print("ERROR:", e)


# ==================== PHONE CHECK (مبدئي) ====================
async def check_phone(phone: str):
    """
    هنا تضع فحص تيليجرام الحقيقي لاحقاً (Telethon / Pyrogram)
    الآن placeholder فقط
    """
    if not phone:
        return "unknown"
    return "clean"


# ==================== APP ====================
def create_user_app(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_user_bot))
    app.add_handler(CallbackQueryHandler(user_bot_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u,c: None))
    return app
