from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],
        [InlineKeyboardButton("🚀 تشغيل البوت", callback_data="start_bot")],
        [InlineKeyboardButton("⛔ إيقاف البوت", callback_data="stop_bot")]
    ])
