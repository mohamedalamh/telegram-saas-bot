from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError
)

from database import save_telegram_account


class LoginManager:

    def __init__(self):
        self.temp_clients = {}

    async def send_code(self, phone, api_id, api_hash):
        """
        إرسال كود تسجيل الدخول.
        """

        client = TelegramClient(
            StringSession(),
            int(api_id),
            api_hash
        )

        await client.connect()

        sent = await client.send_code_request(phone)

        self.temp_clients[phone] = {
            "client": client,
            "phone_code_hash": sent.phone_code_hash,
            "api_id": api_id,
            "api_hash": api_hash,
        }

        return True

    async def login(
        self,
        phone,
        code,
        password=None
    ):
        """
        تسجيل الدخول وإنشاء String Session.
        """

        if phone not in self.temp_clients:
            raise Exception("يجب إرسال الكود أولاً.")

        data = self.temp_clients[phone]

        client = data["client"]

        try:

            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=data["phone_code_hash"]
            )

        except SessionPasswordNeededError:

            if not password:
                return {
                    "status": "PASSWORD_REQUIRED"
                }

            await client.sign_in(password=password)

        except PhoneCodeInvalidError:

            raise Exception("الكود غير صحيح.")

        except PhoneCodeExpiredError:

            raise Exception("انتهت صلاحية الكود.")

        session = client.session.save()

        me = await client.get_me()

        save_telegram_account(
            phone=phone,
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            string_session=session
        )

        await client.disconnect()

        del self.temp_clients[phone]

        return {
            "status": "SUCCESS",
            "phone": phone,
            "user_id": me.id,
            "name": me.first_name,
            "session": session
        }


login_manager = LoginManager()
