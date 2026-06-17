import asyncio

from telethon import functions
from telethon import types
from telethon.errors import (
    FloodWaitError,
    UserPrivacyRestrictedError,
    PhoneNumberBannedError
)

from .telegram_client import TelegramClientManager
from .account_manager import account_manager
from .flood_manager import flood_manager


class TelegramChecker:

    def __init__(self):
        pass

    async def _import_contact(
        self,
        client,
        phone
    ):
        """
        استيراد الرقم إلى جهات الاتصال.
        """

        contact = types.InputPhoneContact(
            client_id=0,
            phone=phone,
            first_name="Checker",
            last_name=""
        )

        result = await client(
            functions.contacts.ImportContactsRequest(
                contacts=[contact]
            )
        )

        return result

    async def _delete_contact(
        self,
        client,
        user
    ):
        """
        حذف جهة الاتصال بعد انتهاء الفحص.
        """

        try:

            await client(
                functions.contacts.DeleteContactsRequest(
                    id=[user]
                )
            )

        except Exception:
            pass

async def check_phone(
        self,
        account,
        phone
    ):
        """
        فحص رقم واحد.
        """

        client = TelegramClientManager(
            account["session"],
            account["api_id"],
            account["api_hash"]
        )

        await client.connect()

        try:

            result = await self._import_contact(
                client,
                phone
            )

        except FloodWaitError as e:

            flood_manager.set_flood(
                account["id"],
                e.seconds
            )

            await client.disconnect()

            return {
                "status": "FLOOD",
                "seconds": e.seconds
            }

        except PhoneNumberBannedError:

            await client.disconnect()

            return {
                "status": "BANNED"
            }

        except Exception as e:

            await client.disconnect()

            return {
                "status": "ERROR",
                "error": str(e)
            }
users = result.users

        if not users:

            await client.disconnect()

            return {
                "status": "NOT_REGISTERED",
                "phone": phone
            }

        user = users[0]

        info = {
            "status": "REGISTERED",
            "phone": phone,
            "telegram_id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "premium": getattr(user, "premium", False),
            "scam": getattr(user, "scam", False),
            "fake": getattr(user, "fake", False),
            "bot": getattr(user, "bot", False),
            "verified": getattr(user, "verified", False),
        }

        try:
            await self._delete_contact(client, user)
        except Exception:
            pass

        await client.disconnect()

        return info
