import asyncio
import logging
from telegram import Bot
from telegram.error import InvalidToken, TelegramError
from user_bot import create_user_app
import database as db

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.running_tasks = {}  # تخزين المهام النشطة {user_id: asyncio.Task}
        self.running_apps = {}   # تخزين تطبيقات البوتات {user_id: Application}

    async def validate_token(self, token: str) -> bool:
        """التحقق من صحة التوكن عبر الاتصال بخوادم تيليجرام"""
        try:
            async with Bot(token) as bot:
                await bot.get_me()
            return True
        except (InvalidToken, TelegramError):
            return False

    async def start_bot(self, user_id: int, token: str) -> bool:
        """تشغيل بوت المستخدم في الخلفية دون حظر السيرفر"""
        if user_id in self.running_tasks:
            return False # البوت يعمل بالفعل

        try:
            app = create_user_app(token)
            await app.initialize()
            await app.updater.start_polling()
            await app.start()
            
            # حفظ التطبيق ومهمة التشغيل المستمر
            self.running_apps[user_id] = app
            self.running_tasks[user_id] = asyncio.create_task(self._run_app_loop(app))
            
            db.set_status(user_id, 1)
            return True
        except Exception as e:
            logger.error(f"Error starting bot for user {user_id}: {e}")
            return False

    async def _run_app_loop(self, app):
        """إبقاء البوت قيد التشغيل والاستماع"""
        try:
            while True:
                await asyncio.sleep(3600) # مهام دورية صامتة
        except asyncio.CancelledError:
            pass

    async def stop_bot(self, user_id: int) -> bool:
        """إيقاف البوت بشكل آمن وتحرير الموارد"""
        if user_id not in self.running_tasks:
            return False

        app = self.running_apps.get(user_id)
        task = self.running_tasks.get(user_id)

        if app:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        
        if task:
            task.cancel()

        self.running_tasks.pop(user_id, None)
        self.running_apps.pop(user_id, None)
        db.set_status(user_id, 0)
        return True

    def get_status(self, user_id: int) -> str:
        """معرفة حالة البوت الحالية"""
        return "🟢 يعمل حالياً" if user_id in self.running_tasks else "🔴 متوقف"

    async def restore_active_bots(self):
        """استعادة كافة البوتات التي كانت تعمل قبل إعادة تشغيل السيرفر"""
        active_bots = db.get_all_active_bots()
        logger.info(f"جاري استعادة {len(active_bots)} من البوتات النشطة...")
        for user_id, token in active_bots:
            asyncio.create_task(self.start_bot(user_id, token))

bot_manager = BotManager()
