from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import db

ADMIN_ID = 123456789  # ضع ايديك هنا

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    db.add_user(user_id)

    if user_id == ADMIN_ID:

        keyboard = [
            [InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")],
            [InlineKeyboardButton("➕ إضافة مستخدم", callback_data="admin_add")],
            [InlineKeyboardButton("❌ حذف مستخدم", callback_data="admin_del")],
            [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")]
        ]

        text = "👑 لوحة تحكم الأدمن"

    else:

        keyboard = [
            [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
            [InlineKeyboardButton("▶️ تشغيل", callback_data="start")],
            [InlineKeyboardButton("⛔ إيقاف", callback_data="stop")],
            [InlineKeyboardButton("📊 حالتي", callback_data="status")]
        ]

        text = "👤 لوحة المستخدم"

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= CALLBACKS =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    data = q.data

    # ================= ADMIN =================
    if uid == ADMIN_ID:

        if data == "admin_users":
            users = db.get_users()
            await q.message.reply_text(f"👥 عدد المستخدمين: {len(users)}")

        elif data == "admin_add":
            context.user_data["add_user"] = True
            await q.message.reply_text("📌 أرسل ID المستخدم")

        elif data == "admin_del":
            context.user_data["del_user"] = True
            await q.message.reply_text("📌 أرسل ID للحذف")

        elif data == "admin_stats":
            users = db.get_users()
            active = len([u for u in users if u[2] == 1])
            await q.message.reply_text(f"📊 الكل: {len(users)}\n🟢 نشط: {active}")

    # ================= USER =================
    else:

        if data == "add_token":
            context.user_data["token"] = True
            await q.message.reply_text("📌 أرسل التوكن")

        elif data == "start":
            db.set_active(uid, 1)
            await q.message.reply_text("🚀 تم التشغيل")

        elif data == "stop":
            db.set_active(uid, 0)
            await q.message.reply_text("⛔ تم الإيقاف")

        elif data == "status":
            user = db.get_user(uid)
            state = "🟢 شغال" if user[2] == 1 else "🔴 متوقف"
            await q.message.reply_text(f"📊 حالتك: {state}")


# ================= TEXT =================
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id
    msg = update.message.text

    # ADD USER
    if context.user_data.get("add_user"):
        db.add_user(int(msg))
        context.user_data["add_user"] = False
        await update.message.reply_text("✅ تمت إضافة المستخدم")

    # DELETE USER
    elif context.user_data.get("del_user"):
        db.delete_user(int(msg))
        context.user_data["del_user"] = False
        await update.message.reply_text("🗑 تم حذف المستخدم")

    # ADD TOKEN
    elif context.user_data.get("token"):
        db.set_token(uid, msg)
        context.user_data["token"] = False
        await update.message.reply_text("✅ تم حفظ التوكن")
