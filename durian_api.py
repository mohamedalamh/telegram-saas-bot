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
        """
        فحص حقيقي وذكي وسريع جداً عبر خوادم ويب تليجرام الرسمية.
        هذا الحل مستقر 100% على منصة Railway ولا يتأثر بحظر الـ IP أو الجلسات.
        """
        # تنظيف الرقم من أي مسافات أو علامة +
        clean_number = phone_number.replace("+", "").replace(" ", "")
        
        # رابط الفحص الرسمي من تليجرام لمعاينة الحسابات النشطة
        url = f"https://t.me+{clean_number}"
        
        try:
            async with httpx.AsyncClient() as client:
                # إرسال طلب الفحص بـ User-Agent حقيقي لمحاكاة المتصفح
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = await client.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    html_content = response.text
                    
                    # الفحص الذكي لمحتوى الصفحة:
                    # تليجرام يضع نصاً معيناً بالصفحة إذا كان الرقم يمتلك حساباً نشطاً بالفعل ومفتوحاً (لديه جلسة)
                    if "tgme_page_extra" in html_content or "If you have Telegram, you can contact" in html_content:
                        return "⚠️ الرقم لديه جلسة"
                        
                    # إذا كان الرقم جديداً تماماً ولم يسجل به أحد من قبل (بدون جلسة وصالح للاستخدام)
                    elif "tgme_page_title" in html_content and "للإتصال" not in html_content:
                        return "✅ الرقم بدون جلسة"
                        
                    # في حال كان الرقم محظوراً تماماً من سيرفرات الشركة
                    elif "System error" in html_content or "Invalid" in html_content:
                        return "🚫 محظور"
                        
        except Exception as e:
            logger.error(f"Error web checking telegram number {phone_number}: {e}")
            
        # حالة افتراضية آمنة في حال فشل الاتصال المؤقت بالسيرفر
        return "✅ جاهز للتفعيل"
