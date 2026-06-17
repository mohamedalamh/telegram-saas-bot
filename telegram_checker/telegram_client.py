from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import asyncio


class TelegramClientManager:
    def __init__(self):
        self.clients = {}

    async def get_client(self, account):
        """
        account = {
            "id":1,
            "api_id":12345,
            "api_hash":"xxxxx",
            "session":"xxxxx"
        }
        """

        account_id = account["id"]

        if account_id in self.clients:
            client = self.clients[account_id]

            if await client.is_user_authorized():
                return client

            try:
                await client.connect()

                if await client.is_user_authorized():
                    return client

            except Exception:
                pass

        client = TelegramClient(
            StringSession(account["session"]),
            int(account["api_id"]),
            account["api_hash"]
        )

        await client.connect()

        if not await client.is_user_authorized():
            raise Exception("Telegram session is not authorized.")

        self.clients[account_id] = client

        return client

    async def disconnect_client(self, account_id):
        if account_id not in self.clients:
            return

        try:
            await self.clients[account_id].disconnect()
        except Exception:
            pass

        self.clients.pop(account_id, None)

    async def disconnect_all(self):
        for account_id in list(self.clients.keys()):
            try:
                await self.clients[account_id].disconnect()
            except Exception:
                pass

        self.clients.clear()


telegram_client_manager = TelegramClientManager()
