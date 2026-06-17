import asyncio
import logging

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self):
        # طابور الأرقام التي تنتظر الفحص
        self._queue = asyncio.Queue()
        # مجموعة لتتبع الأرقام الموجودة حالياً في الطابور لمنع التكرار
        self._tracked_phones = set()

    async def add_to_queue(self, phone: str):
        """إضافة رقم هاتف جديد إلى طابور الفحص إذا لم يكن موجوداً بالفعل"""
        clean_phone = phone.strip().replace("+", "")
        if clean_phone not in self._tracked_phones:
            self._tracked_phones.add(clean_phone)
            await self._queue.put(clean_phone)
            logger.info(f"📍 تم إضافة الرقم {clean_phone} إلى طابور الفحص تلقائياً.")
            return True
        return False

    async def get_next_phone(self) -> str:
        """سحب الرقم التالي من الطابور للبدء في فحصه"""
        phone = await self._queue.get()
        if phone in self._tracked_phones:
            self._tracked_phones.remove(phone)
        return phone

    def is_empty(self) -> bool:
        """التحقق مما إذا كان طابور الفحص فارغاً"""
        return self._queue.empty()

    def queue_size(self) -> int:
        """جلب عدد الأرقام المنتظرة في الطابور حالياً"""
        return self._queue.qsize()

    def clear_queue(self):
        """تفريغ الطابور بالكامل"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self._tracked_phones.clear()
        logger.info("🗑️ تم تفريغ طابور فحص الأرقام بالكامل.")

# إنشاء وإخراج الكائن العام المتوافق مع ملف __init__.py بمحاذاة الصفر تماماً
queue_manager = QueueManager()
