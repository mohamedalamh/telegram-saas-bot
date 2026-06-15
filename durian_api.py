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
                    try:
                        data = response.json()
                        if isinstance(data, dict) and data.get("code") == 200 and "data" in data:
                            user_data = data["data"]
                            if isinstance(user_data, dict):
                                return float(user_data.get("score", 0.0))
                    except ValueError:
                        pass
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
        return 0.0

    @staticmethod
    async def order_number_by_name(username: str, api_key: str, country_code: str, project_id: str = "0257") -> dict:
        """طلب سحب رقم تليجرام مخصص بناءً على واجهة getMobile الرسمية بأمان وتوافق تام"""
        url = (
            f"{BASE_URL}/getMobile?name={username}&ApiKey={api_key}"
            f"&cuy={country_code}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError:
                        # في حال أرجع السيرفر نصاً صريحاً بالكامل
                        return {"status": "error", "message": response.text}
                    
                    # التحقق من أن الاستجابة الرئيسية عبارة عن قاموس
                    if isinstance(data, dict) and data.get("code") == 200 and "data" in data:
                        mobile_data = data["data"]
                        
                        # حماية حاسمة: إذا كان الموقع يضع نصاً داخل data عند نفاد الأرقام
                        if isinstance(mobile_data, str):
                            logger.warning(f"⚠️ السيرفر أرجع رسالة نصية داخل حقل البيانات لدولة [{country_code}]: {mobile_data}")
                            return {"status": "error", "message": mobile_data}
                        
                        # إذا كانت البيانات مصفوفة/قائمة (ليست شائعة ولكن للاحتياط)
                        if isinstance(mobile_data, list) and len(mobile_data) > 0:
                            mobile_data = mobile_data[0]
                        
                        # التأكد أخيراً أن المتغير أصبح قاموساً لنتمكن من استخدام .get() بأمان
                        if isinstance(mobile_data, dict):
                            return {
                                "status": "success", 
                                "number": mobile_data.get("mobile"), 
                                "order_id": mobile_data.get("orderId") or mobile_data.get("id") or mobile_data.get("serialNo")
                            }
                        
                    # إذا لم تكن البيانات مطابقة لشروط النجاح
                    msg = data.get("msg") if isinstance(data, dict) else "No numbers available"
                    return {"status": "error", "message": msg}
                    
        except Exception as e:
            logger.error(f"Error ordering number for country {country_code}: {e}")
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def cancel_order(username: str, api_key: str, order_id: str) -> bool:
        """إلغاء الطلب وتحرير الرصيد في حال كان الرقم محظوراً أو تالفاً"""
        url = f"{BASE_URL}/addBlack?name={username}&ApiKey={api_key}&serialNo={order_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and (data.get("code") == 200 or "success" in str(data).lower()):
                            logger.info(f"✅ Successfully canceled order {order_id} on Durian.")
                            return True
                    except ValueError:
                        if "success" in response.text.lower() or "ok" in response.text.lower():
                            return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
        return False

    @staticmethod
    async def get_balance(api_key: str) -> float:
        """دالة توافقية ممتدة لتفادي أخطاء الاستدعاء القديمة"""
        return 0.0
