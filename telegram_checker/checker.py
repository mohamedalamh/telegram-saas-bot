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

async def get_available_account(self):
        """
        الحصول على أول حساب متاح للفحص.
        """

        accounts = account_manager.get_available_accounts()

        if not accounts:
            return None

        for account in accounts:

            if flood_manager.is_flooded(account["id"]):
                continue

            return account

        return None

async def wait_for_account(self):
        """
        الانتظار حتى يصبح هناك حساب متاح.
        """

        while True:

            account = await self.get_available_account()

            if account:
                return account

            await asyncio.sleep(5)

async def check_numbers(
        self,
        phones,
        callback=None
    ):
        """
        فحص مجموعة أرقام.
        """

        results = []

        for phone in phones:

            account = await self.wait_for_account()

            result = await self.check_phone(
                account,
                phone
            )

            if result["status"] == "FLOOD":
                continue

            if result["status"] == "BANNED":
                account_manager.disable_account(account["id"])
                continue

            results.append(result)

            if callback:
                await callback(result)

        return results

class BatchChecker:

    def __init__(self, checker):
        self.checker = checker

    async def worker(
        self,
        account,
        queue,
        callback=None
    ):
        """
        عامل يستخدم حساب Telegram واحد.
        """

        while True:

            try:
                phone = await queue.get()

            except asyncio.CancelledError:
                break

            if phone is None:
                queue.task_done()
                break

            result = await self.checker.check_phone(
                account,
                phone
            )

            if result["status"] == "FLOOD":

                flood_manager.set_flood(
                    account["id"],
                    result["seconds"]
                )

                queue.put_nowait(phone)

                queue.task_done()
                break

            elif result["status"] == "BANNED":

                account_manager.disable_account(
                    account["id"]
                )

                queue.put_nowait(phone)

                queue.task_done()
                break

            if callback:
                await callback(result)

            queue.task_done()

async def run(
        self,
        phones,
        callback=None
    ):
        """
        تشغيل الفحص المتوازي.
        """

        queue = asyncio.Queue()

        for phone in phones:
            await queue.put(phone)

        accounts = account_manager.get_available_accounts()

        workers = []

        for account in accounts:

            if flood_manager.is_flooded(account["id"]):
                continue

            task = asyncio.create_task(

                self.worker(
                    account,
                    queue,
                    callback
                )

            )

            workers.append(task)

        await queue.join()

        for _ in workers:
            await queue.put(None)

        await asyncio.gather(
            *workers,
            return_exceptions=True
        )

        return True

telegram_checker = TelegramChecker()

batch_checker = BatchChecker(
    telegram_checker
)
