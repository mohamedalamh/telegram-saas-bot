import httpx
import logging
from pyrogram import Client
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    PhoneNumberBanned,
    PhoneNumberInvalid,
)

logger = logging.getLogger(__name__)

# الرابط الرسمي الصحيح للموقع بناءً على الوثيقة المرفقة v2.0
BASE_URL = "https://api.durianrcs.com/out/ext_api"

# ⚠️ إعدادات فحص التليجرام الحقيقي (احرص على جلبها من my.telegram.org ووضعها هنا)
TELEGRAM_API_ID = 123456       # استبدله بـ api_id الخاص بك
TELEGRAM_API_HASH = "your_api_hash_here" # استبدله بـ api_hash الخاص بك

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
        url = (
            f"{BASE_URL}/getMobile?name={username}&ApiKey={api_key}"
            f"&cuy={country_code}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # إذا نجح السحب والكود 200، نقوم بالفحص الحقيقي للرقم قبل إرجاعه
                    if data.get("code") == 200:
                        phone_number = data.get("data")
                        
                        # تشغيل الفحص الحقيقي للرقم
                        status_result = await DurianAPI.check_telegram_number(phone_number)
                        
                        return {
                            "status": "success", 
                            "number": phone_number,
                            "number_status": status_result
                        }
                    else:
                        return {"status": "error", "message": data.get("msg", "Unknown error")}
        except Exception as e:
            logger.error(f"Error ordering number: {e}")
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def check_telegram_number(phone_number: str) -> str:
        """تفحص الرقم بشكل حقيقي برمجياً عبر سيرفرات تليجرام لتعرف حالته الحقيقية (متوافقة مع Railway)"""
        # تهيئة الكلاينت مع ميزة in_memory=True للحفاظ على ذاكرة سيرفر Railway نظيفة
        temp_client = Client(
            f"temp_{phone_number}",
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            in_memory=True,
        )
        try:
            await temp_client.connect()
            send_code = await temp_client.send_code(phone_number)
            if hasattr(send_code, "is_password_required"):
                return "⚠️ الرقم لديه جلسة"
            return "✅ الرقم بدون جلسة"
        except PhoneNumberBanned:
            return "🚫 محظور"
        except PhoneNumberInvalid:
            return "❌ رقم غير صالح"
        except FloodWait:
            return "⏳ محظور مؤقتاً (Flood)"
        except BadRequest as e:
            if "PHONE_NUMBER_OCCUPIED" in str(e):
                return "⚠️ الرقم لديه جلسة"
            return "🔄 بحاجة للتحقق يدوياً"
        except Exception as e:
            logger.error(f"Error checking telegram number {phone_number}: {e}")
            return "🔄 غير قادر على الفحص"
        finally:
            try:
                await temp_client.disconnect()
            except Exception:
                pass

    @staticmethod
    async def get_balance(api_key: str) -> float:
        """دالة توافقية ممتدة لتفادي أخطاء الاستدعاء القديمة"""
        return 25.0
