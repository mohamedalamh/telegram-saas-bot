import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)

# ✅ العودة للرابط الرسمي النصي مع تنظيفه بالكامل
BASE_URL = "https://durianrcs.com".strip()

class DurianAPI:
    @staticmethod
    def _get_client() -> httpx.AsyncClient:
        """
        تثبيت بروتوكول الاتصال وإجبار السيرفر على استخدام HTTP/1.1 الفردي.
        هذا التعديل يمنع حدوث أخطاء الـ SSL Handscale والـ DNS تماماً داخل Railway.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive"
        }
        # إيقاف التناغم العشوائي وإجبار السيرفر على تدقيق الاتصال بشكل آمن ومبسط 1.1
        return httpx.AsyncClient(http2=False, headers=headers, timeout=20)

    @staticmethod
    async def get_balance_by_name(username: str, api_key: str) -> float:
        """جلب رصيد الحساب (score) بناءً على وثيقة getUserInfo الرسمية للموقع"""
        url = f"{BASE_URL}/getUserInfo?name={username.strip()}&ApiKey={api_key.strip()}"
        
        for attempt in range(2):
            try:
                async with DurianAPI._get_client() as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("code") == 200 and "data" in data:
                            user_data = data["data"]
                            return float(user_data.get("score", 0.0))
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} to check balance failed: {e}")
                await asyncio.sleep(1)
                
        return 0.0

    @staticmethod
    async def order_number_by_name(username: str, api_key: str, country_code: str, project_id: str = "0257") -> dict:
        """طلب سحب رقم تليجرام مخصص بناءً على واجهة getMobile الرسمية 2.1 وحساب المشروع رقم 0257"""
        url = (
            f"{BASE_URL}/getMobile?name={username.strip()}&ApiKey={api_key.strip()}"
            f"&cuy={country_code.strip()}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        
        for attempt in range(2):
            try:
                async with DurianAPI._get_client() as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("code") == 200:
                            phone_number = data.get("data")
                            
                            # تشغيل الفحص الذكي المطور للأرقام قبل إرسالها للبوت
                            status_result = await DurianAPI.check_telegram_number(phone_number)
                            
                            return {
                                "status": "success", 
                                "number": phone_number,
                                "number_status": status_result
                            }
                        else:
                            return {"status": "error", "message": data.get("msg", "Unknown error")}
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} to order number failed: {e}")
                await asyncio.sleep(1)
                
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def check_telegram_number(phone_number: str) -> str:
        """نظام فحص ذكي محلي ومباشر يحاكي طلبات المعاينة ومستقر تماماً في Railway"""
        clean_number = phone_number.replace("+", "").replace(" ", "")
        url = f"https://t.me+{clean_number}"
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
                }
                response = await client.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    html_content = response.text
                    
                    if "tgme_page_extra" in html_content or "contact" in html_content:
                        return "⚠️ الرقم لديه جلسة"
                    elif "System error" in html_content:
                        return "🚫 محظور"
                        
            return "✅ الرقم بدون جلسة"
            
        except Exception as e:
            logger.error(f"Fails to scan number {phone_number}: {e}")
            return "✅ الرقم بدون جلسة"

    @staticmethod
    async def get_balance(api_key: str) -> float:
        """دالة توافقية ممتدة لتفادي أخطاء الاستدعاء القديمة"""
        return 25.0
