from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import db

ADMIN_ID = 123456789  # 🔴 ضع ايديك هنا

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    db.add_user(user_id)

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("👥 المستخدمين", callback_data="users")],
            [InlineKeyboardButton("➕ إضافة مستخدم", callback_data="add_user")]
        ]
        text = "👑 لوحة الأدمن"
    else:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
            [InlineKeyboardButton("▶️ تشغيل", callback_data="start")],
            [InlineKeyboardButton("⛔ إيقاف", callback_data="stop")]
        ]
        text = "👤 لوحة المستخدم"

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ================= BUTTONS =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # ===== ADMIN =====
    if user_id == ADMIN_ID:

        if data == "users":
            users = db.get_all_users()
            await query.message.reply_text(f"👥 عدد المستخدمين: {len(users)}")

        elif data == "add_user":
            context.user_data["add_user"] = True
            await query.message.reply_text("📌 أرسل ايدي المستخدم")

    # ===== USER =====
    else:

        if data == "add_token":
            context.user_data["add_token"] = True
            await query.message.reply_text("📌 أرسل التوكن")

        elif data == "start":
            db.set_active(user_id, 1)
            await query.message.reply_text("🚀 تم التشغيل")

        elif data == "stop":
            db.set_active(user_id, 0)
            await query.message.reply_text("⛔ تم الإيقاف")


# ================= TEXT =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    # ADD USER (ADMIN)
    if context.user_data.get("add_user"):
        db.add_user(int(text))
        context.user_data["add_user"] = False
        await update.message.reply_text("✅ تم إضافة المستخدم")

    # ADD TOKEN (USER)
    elif context.user_data.get("add_token"):
        db.set_token(user_id, text)
        context.user_data["add_token"] = False
        await update.message.reply_text("✅ تم حفظ التوكن")
