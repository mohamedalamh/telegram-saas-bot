from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from .account_manager import account_manager
from .login_manager import login_manager
from .checker import batch_checker

(
    API_ID,
    API_HASH,
    PHONE,
    CODE,
    PASSWORD,
    UPLOAD_FILE,
) = range(6)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [
            InlineKeyboardButton(
                "➕ إضافة حساب",
                callback_data="add_account"
            )
        ],

        [
            InlineKeyboardButton(
                "📱 الحسابات",
                callback_data="accounts"
            )
        ],

        [
            InlineKeyboardButton(
                "📂 رفع ملف",
                callback_data="upload_file"
            )
        ],

        [
            InlineKeyboardButton(
                "▶️ بدء الفحص",
                callback_data="start_check"
            )
        ],

        [
            InlineKeyboardButton(
                "📊 الإحصائيات",
                callback_data="stats"
            )
        ]

    ]

    await update.message.reply_text(

        "اختر العملية المطلوبة",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )

async def add_account_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(

        "أرسل API_ID"

    )

    return API_ID

async def receive_api_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user.id

    if user not in user_data:
        user_data[user] = {}

    user_data[user]["api_id"] = update.message.text.strip()

    await update.message.reply_text(

        "الآن أرسل API_HASH"

    )

    return API_HASH

async def receive_api_hash(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user.id

    user_data[user]["api_hash"] = update.message.text.strip()

    await update.message.reply_text(

        "أرسل رقم الهاتف"

    )

    return PHONE

async def receive_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user.id

    phone = update.message.text.strip()

    user_data[user]["phone"] = phone

    try:

        await login_manager.send_code(
            phone=phone,
            api_id=user_data[user]["api_id"],
            api_hash=user_data[user]["api_hash"]
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ حدث خطأ:\n\n{e}"
        )

        return ConversationHandler.END

    await update.message.reply_text(

        "✅ تم إرسال كود تسجيل الدخول.\n\n"
        "أرسل الكود الذي وصلك."

    )

    return CODE

async def receive_code(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user.id

    code = update.message.text.strip()

    try:

        result = await login_manager.login(

            phone=user_data[user]["phone"],

            code=code

        )

    except Exception as e:

        await update.message.reply_text(

            f"❌ {e}"

        )

        return ConversationHandler.END

    if result["status"] == "PASSWORD_REQUIRED":

        await update.message.reply_text(

            "🔐 الحساب يحتوي على تحقق بخطوتين.\n\n"
            "أرسل كلمة المرور."

        )

        return PASSWORD

    await update.message.reply_text(

        f"✅ تم إضافة الحساب بنجاح.\n\n"
        f"الاسم: {result['name']}\n"
        f"الرقم: {result['phone']}"

    )

    del user_data[user]

    return ConversationHandler.END

async def receive_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user.id

    password = update.message.text.strip()

    try:

        result = await login_manager.login(

            phone=user_data[user]["phone"],

            code="",

            password=password

        )

    except Exception as e:

        await update.message.reply_text(

            f"❌ {e}"

        )

        return ConversationHandler.END

    await update.message.reply_text(

        f"✅ تم إضافة الحساب.\n\n"
        f"{result['name']}"

    )

    del user_data[user]

    return ConversationHandler.END
