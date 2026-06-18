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
        logger.info(f"[TRACE] DurianAPI.order_number_by_name: Final URL generated: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                logger.info(f"[TRACE] DurianAPI Response: Status={response.status_code}, RawBody={response.text}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        extracted_num = data.get("data")
                        logger.info(f"[TRACE] DurianAPI Success: Extracted Number: {extracted_num}")
                        return {"status": "success", "number": extracted_num}
                    else:
                        logger.warning(f"[TRACE] DurianAPI Logic Error: Code={data.get('code')}, Msg={data.get('msg')}")
                        return {"status": "error", "message": data.get("msg", "Unknown error")}
                else:
                    logger.error(f"[TRACE] DurianAPI HTTP Error: Status={response.status_code}")
        except Exception as e:
            logger.error(f"[TRACE] DurianAPI Exception: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def get_sms(username: str, api_key: str, phone_number: str, project_id: str = "0257") -> dict:
        """جلب كود التحقق (SMS) للرقم المطلوب بناءً على واجهة getSms"""
        # تنظيف الرقم من علامة الزائد إذا وجدت
        clean_phone = phone_number.replace("+", "")
        url = f"{BASE_URL}/getSms?name={username}&ApiKey={api_key}&phone={clean_phone}&pid={project_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        return {"status": "success", "sms": data.get("data")}  # يرجع نص الرسالة أو الكود مباشرة
                    else:
                        return {"status": "waiting", "message": data.get("msg", "قيد الانتظار")}
        except Exception as e:
            logger.error(f"Error getting SMS for {phone_number}: {e}")
        return {"status": "error", "message": "فشل الاتصال بالسيرفر"}

    @staticmethod
    async def cancel_number(username: str, api_key: str, phone_number: str, project_id: str = "0257") -> bool:
        """إلغاء الرقم وتحريره (بسبب حظر أو عدم وصول كود) بناءً على واجهة cancelMobile"""
        clean_phone = phone_number.replace("+", "")
        url = f"{BASE_URL}/cancelMobile?name={username}&ApiKey={api_key}&phone={clean_phone}&pid={project_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("code") == 200
        except Exception as e:
            logger.error(f"Error canceling number {phone_number}: {e}")
        return False

    @staticmethod
    async def get_balance(username: str, api_key: str) -> float:
        """جلب رصيد الحساب الحقيقي من واجهة البرمجة"""
        return await DurianAPI.get_balance_by_name(username, api_key)
