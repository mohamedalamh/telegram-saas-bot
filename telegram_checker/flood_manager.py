from datetime import datetime, timedelta

from database import (
    set_account_flood,
    increase_account_checks,
    get_account_flood
)


class FloodManager:

    async def is_flooded(self, account_id):
        """
        التحقق من حالة الحظر المؤقت (FloodWait).
        """
        flood_until = get_account_flood(account_id)
        if not flood_until:
            return False
        return datetime.utcnow() < flood_until

    async def set_flood(self, account_id, seconds):
        """
        عند دخول الحساب FloodWait.
        """

        flood_until = datetime.utcnow() + timedelta(seconds=seconds)

        set_account_flood(
            account_id,
            flood_until
        )

    async def account_used(self, account_id):
        """
        زيادة عداد الفحص.
        """

        increase_account_checks(account_id)

    async def account_ok(self, account_id):
        """
        حالياً لا نحتاج أي شيء هنا.
        """

        return True


flood_manager = FloodManager()
