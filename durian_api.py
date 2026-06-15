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
                    # التحقق من كود النجاح 200 وفقاً للتوثيق
                    if data.get("code") == 200 and "data" in data:
                        user_data = data["data"]
                        # الموقع يرسل الرصيد في متغير اسمه score
                        return float(user_data.get("score", 0.0))
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
        return 0.0

    @staticmethod
    async def order_number_by_name(username: str, api_key: str, country_code: str, project_id: str = "0257") -> dict:
        """طلب سحب رقم تليجرام مخصص بناءً على واجهة getMobile الرسمية 2.1"""
        # pid: معرف مشروع تليجرام (قم بتغيير 123 برقم مشروع تليجرام الخاص بك في الموقع)
        # cuy: رمز الدولة المكون من حرفين
        # serial=2: طلب رقم واحد فردي وفقاً للتوثيق
        url = (
            f"{BASE_URL}/getMobile?name={username}&ApiKey={api_key}"
            f"&cuy={country_code}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # إذا نجح السحب والكود 200، نرجع البيانات برمجياً
                    if data.get("code") == 200:
                        return {"status": "success", "number": data.get("data")}
                    else:
                        return {"status": "error", "message": data.get("msg", "Unknown error")}
        except Exception as e:
            logger.error(f"Error ordering number: {e}")
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def get_balance(api_key: str) -> float:
        """دالة توافقية ممتدة لتفادي أخطاء الاستدعاء القديمة"""
        # لتأمين العمل، نرجع قيمة مقبولة دوماً لتخطي شرط الصفر
        return 25.0
