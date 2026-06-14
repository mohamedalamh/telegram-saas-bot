from telegram_checker import TelegramChecker
import os

checker = TelegramChecker(
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

async def check_phone(phone):
    result = await checker.check(phone)

    if result["status"] == "banned":
        return "❌ محظور"
    elif result["status"] == "used":
        return "⚠️ مستخدم / لديه جلسة"
    else:
        return "✅ جديد"
