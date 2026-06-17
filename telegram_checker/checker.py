from telethon.errors import FloodWaitError
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

from telegram_checker.telegram_client import telegram_client_manager
from telegram_checker.account_manager import account_manager
from telegram_checker.flood_manager import flood_manager


async def check_phone(phone):
    """
    فحص رقم بواسطة Telegram.

    يرجع:

    {
        "status":"NEW",
        "text":"✅ جديد بدون جلسة"
    }

    أو

    {
        "status":"USED",
        "text":"⚠️ عليه جلسة"
    }

    أو

    {
        "status":"BANNED",
        "text":"🚫 محظور"
    }
    """

    account = await account_manager.get_available_account()

    if account is None:

        raise Exception("لا يوجد أي حساب Telegram متاح للفحص.")

    client = await telegram_client_manager.get_client(account)

    try:

        contact = InputPhoneContact(
            client_id=0,
            phone=phone,
            first_name="Check",
            last_name=""
        )

        result = await client(
            ImportContactsRequest([contact])
        )

        await flood_manager.account_used(account["id"])

        # سنضيف تحليل النتيجة في الخطوة القادمة

        return result

    except FloodWaitError as e:

        await flood_manager.set_flood(
            account["id"],
            e.seconds
        )

        return await check_phone(phone)

    except Exception:
        raise
