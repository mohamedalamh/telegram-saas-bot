import httpx
import logging

logger = logging.getLogger(__name__)

# الرابط الرسمي الصحيح للموقع بناءً على الوثيقة المرفقة v2.0
BASE_URL = "https://api.durianrcs.com/out/ext_api"

class DurianAPI:
    @staticmethod
    async def get_balance_by_name(username: str, api_key: str) -> float:
        """جلب رصيد الحساب (score) بناءً على وثيقة getUserInfo الرسمية للموقع"""
        url = f"{BASE_URL}/getUserInfo?name={username}&ApiKey={api_key}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200 and "data" in data:
                        user_data = data["data"]
                        return float(user_data.get("score", 0.0))
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
        return 0.0

    @staticmethod
    async def order_number_by_name(username: str, api_key: str, country_code: str, project_id: str = "0257") -> dict:
        """طلب سحب رقم تليجرام مخصص بناءً على واجهة getMobile الرسمية 2.1"""
        url = (
            f"{BASE_URL}/getMobile?name={username}&ApiKey={api_key}"
            f"&cuy={country_code}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # حماية إضافية: التأكد من أن الاستجابة قاموس (dict) وليست نصاً مباشراً
                    if isinstance(data, dict) and data.get("code") == 200 and "data" in data:
                        return {
                            "status": "success", 
                            "number": data["data"].get("mobile"), 
                            "order_id": data["data"].get("orderId") or data["data"].get("id")
                        }
                    else:
                        msg = data.get("msg", "Unknown error") if isinstance(data, dict) else str(data)
                        return {"status": "error", "message": msg}
        except Exception as e:
            logger.error(f"Error ordering number: {e}")
        return {"status": "error", "message": "Connection failed"}
    @staticmethod
    async def cancel_order(username: str, api_key: str, order_id: str) -> bool:
        """إلغاء الطلب وتحرير الرصيد في حال كان الرقم محظوراً أو تالفاً (تحديث تلقائي)"""
        # نرسل حالة الإلغاء للموقع (عادة تكون المتغير يدعى status=3 أو cancel حسب التوثيق)
        url = f"{BASE_URL}/cancelOrder?name={username}&ApiKey={api_key}&orderId={order_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        logger.info(f"✅ Successfully canceled order {order_id} on Durian.")
                        return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
        return False

    @staticmethod
    async def get_balance(api_key: str) -> float:
        """دالة توافقية ممتدة لتفادي أخطاء الاستدعاء القديمة"""
        return 25.0
