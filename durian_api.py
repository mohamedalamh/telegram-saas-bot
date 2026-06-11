import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://durianrcs.com"

class DurianAPI:
    @staticmethod
    async def get_balance(api_key: str) -> float:
        """جلب رصيد الحساب للتأكد من عمل الـ API"""
        url = f"{BASE_URL}/user/balance?api_key={api_key}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        return float(data.get("balance", 0.0))
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
        return 0.0

    @staticmethod
    async def order_number(api_key: str, country: str, service: str = "telegram") -> dict:
        """طلب شراء رقم جديد"""
        url = f"{BASE_URL}/order/get?api_key={api_key}&country={country}&service={service}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error ordering number: {e}")
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def check_sms(api_key: str, order_id: str) -> dict:
        """الفحص الدوري عن وصول كود الـ SMS للرقم المطلق"""
        url = f"{BASE_URL}/order/sms?api_key={api_key}&order_id={order_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error checking SMS: {e}")
        return {"status": "error"}
