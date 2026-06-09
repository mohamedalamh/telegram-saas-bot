from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():

    keyboard = [

        [InlineKeyboardButton("➕ إضافة توكن", callback_data="add_token")],

        [InlineKeyboardButton("▶ تشغيل البوت", callback_data="start_bot")],

        [InlineKeyboardButton("⏹ إيقاف البوت", callback_data="stop_bot")],

        [InlineKeyboardButton("⚙ الإعدادات", callback_data="settings")],

        [InlineKeyboardButton("💳 الاشتراك", callback_data="subscription")]

    ]

    return InlineKeyboardMarkup(keyboard)
