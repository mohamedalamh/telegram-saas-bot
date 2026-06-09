from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🔑 إضافة توكن البوت", callback_data="add_token")],
        [InlineKeyboardButton("✅ تشغيل البوت", callback_data="start_bot")],
        [InlineKeyboardButton("❌ إيقاف البوت", callback_data="stop_bot")],
        [InlineKeyboardButton("📋 حالة البوت", callback_data="status")],
        [InlineKeyboardButton("📞 الدعم", callback_data="support")]
    ]

    return InlineKeyboardMarkup(keyboard)
