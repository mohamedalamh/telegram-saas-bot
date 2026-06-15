import httpx
import logging

logger = logging.getLogger(__name__)

# الرابط الرسمي الصحيح للموقع
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
                            return float(user_data.get("score", 0.0))
                    except ValueError:
                        logger.error(f"UserInfo returned non-JSON response: {response.text}")
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
        return 0.0

    @staticmethod
    async def order_number_by_name(username: str, api_key: str, country_code: str, project_id: str = "0257") -> dict:
        """طلب سحب رقم تليجرام مخصص بناءً على واجهة getMobile الرسمية بأمان تام"""
        url = (
            f"{BASE_URL}/getMobile?name={username}&ApiKey={api_key}"
            f"&cuy={country_code}&pid={project_id}&num=1&noblack=0&serial=2"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    raw_text = response.text.strip()
                    
                    # محاولة تحويل النص إلى JSON بأمان دون إحداث انهيار للمكتبة
                    try:
                        data = response.json()
                    except ValueError:
                        # هنا يتم اصطياد النصوص الصريحة مثل (Balance not enough أو لا توجد أرقام)
                        logger.warning(f"⚠️ الموقع أرجع استجابة نصية للدولة [{country_code}]: {raw_text}")
                        return {"status": "error", "message": raw_text}

                    # التأكد من أن البيانات عبارة عن قاموس صالح
                    if isinstance(data, dict):
                        if data.get("code") == 200 and "data" in data and data["data"]:
                            mobile_data = data["data"]
                            # بعض ردود الموقع ترجع البيانات داخل قائمة أو قاموس مباشر، نتحقق من الطرفين
                            if isinstance(mobile_data, list) and len(mobile_data) > 0:
                                mobile_data = mobile_data[0]
                                
                            return {
                                "status": "success", 
                                "number": mobile_data.get("mobile"), 
                                "order_id": mobile_data.get("orderId") or mobile_data.get("id") or mobile_data.get("serialNo")
                            }
                        else:
                            msg = data.get("msg") or data.get("message") or "No numbers available"
                            return {"status": "error", "message": msg}
                    else:
                        return {"status": "error", "message": str(raw_text)}
                        
        except Exception as e:
            logger.error(f"Error ordering number for country {country_code}: {e}", exc_info=True)
        return {"status": "error", "message": "Connection failed"}

    @staticmethod
    async def cancel_order(username: str, api_key: str, order_id: str) -> bool:
        """إلغاء الطلب وتحرير الرصيد أو حظر الرقم التالف عبر واجهة addBlack الرسمية لـ Durian"""
        # الروابط الشائعة لإلغاء الأرقام في السيرفر الصيني هي addBlack لتجنب نزول نفس الرقم مجدداً
        url = f"{BASE_URL}/addBlack?name={username}&ApiKey={api_key}&serialNo={order_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and (data.get("code") == 200 or "success" in str(data).lower()):
                            logger.info(f"✅ Successfully canceled/blacklisted order {order_id} on Durian.")
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
