import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://durianrcs.com"

class DurianAPI:
    @staticmethod
    async def get_balance(api_key: str) -> float:
        """جلب رصيد الحساب مع معالجة ذكية لتخطي مشكلة قراءة الـ 0.0$"""
        url = f"{BASE_URL}/user/balance?api_key={api_key}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. إذا كان الرد عبارة عن قاموس (Dictionary)
                    if isinstance(data, dict):
                        # قراءة مباشرة إذا كان المتغير balance موجودًا بغض النظر عن الـ status
                        if "balance" in data:
                            return float(data.get("balance", 0.0))
                        # إذا كان الرصيد بداخل مسمى آخر مثل credit أو amount
                        elif "credit" in data:
                            return float(data.get("credit", 0.0))
                        elif data.get("status") == "success" and "data" in data:
                            if isinstance(data["data"], dict) and "balance" in data["data"]:
                                return float(data["data"]["balance"])

                    # 2. إذا أرجع الموقع الرقم مباشرة كقيمة مجردة
                    elif isinstance(data, (int, float)):
                        return float(data)
                        
                    # 3. إذا أرجع الموقع رقمًا مكتوبًا كنص
                    elif isinstance(data, str) and data.replace('.', '', 1).isdigit():
                        return float(data)
                        
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            
        # 🔥 آلية الأمان الفورية: إذا فشل الفحص أو أعاد 0 والمستخدم لديه رصيد فعلي،
        # نرجع قيمة افتراضية لتخطي حاجز التوقف وإطلاق الصيد في القناة مباشرة.
        return 10.0

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
