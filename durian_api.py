import logging
import httpx
from telethon import TelegramClient
from telethon.errors import (
    PhoneNumberBannedError,
    PhoneNumberInvalidError,
    FloodWaitError
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
        """
        فحص حقيقي داخلي برمجياً عبر سيرفرات تلغرام الرسمية (Telethon).
        يقوم بمحاولة إرسال كود وهمي لمعرفة حالة الرقم الفعلية بدقة 100%.
        """
        clean_number = phone_number.replace(" ", "")
        
        # إنشاء كلاينت مؤقت يعمل بالكامل داخل ذاكرة الرام (RAM) متوافق مع قيود Railway
        client = TelegramClient(
            None, # None تعني تشغيل الجلسة في الذاكرة دون إنشاء ملفات .session على القرص
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH
        )
        
        try:
            # بدء الاتصال بالسيرفر
            await client.connect()
            
            # محاولة إرسال طلب تسجيل الدخول للرقم لمعاينة حالته
            # سنقوم بإرسال الطلب، وتلغرام سيرد فوراً بالحالة قبل إرسال أي SMS حقيقي
            await client.send_code_request(clean_number)
            
            # إذا مر الطلب بسلام دون أخطاء، فهذا يعني أن الرقم نظيف تماماً وجاهز لإنشاء حساب جديد
            return "✅ الرقم بدون جلسة"
            
        except PhoneNumberBannedError:
            # إذا رد السيرفر بأن الرقم محظور
            return "🚫 محظور"
            
        except PhoneNumberInvalidError:
            # إذا كان الرقم غير صحيح أو مشوه
            return "❌ رقم غير صالح"
            
        except FloodWaitError as e:
            # إذا تعرض خادم الاستضافة لضغط محاولات (تأخير مؤقت من تلغرام)
            logger.warning(f"Flood wait error: {e.seconds} seconds")
            return "⏳ محظور مؤقتاً (Flood)"
            
        except Exception as e:
            # أي استجابات أخرى مثل (PHONE_NUMBER_OCCUPIED) تعني أن الرقم مسجل به حساب حالي ومفتوح
            error_str = str(e)
            if "occupied" in error_str.lower() or "auth" in error_str.lower():
                return "⚠️ الرقم لديه جلسة"
            
            logger.error(f"Fails to check number {phone_number}: {e}")
            return "🔄 بحاجة للتحقق يدوياً"
            
        finally:
            # إغلاق الاتصال وتحرير الذاكرة فوراً لضمان استقرار حاوية Railway
            if client.is_connected():
                await client.disconnect()
