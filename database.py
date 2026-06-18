import os
import time
import logging
import pg8000
from urllib.parse import urlparse

# إعداد الـ Logger لضمان تسجيل أخطاء قاعدة البيانات بدقة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """الاتصال الآمن والمباشر بسيرفر Neon بالتفكيك البرمجي الداخلي مع آلية إعادة محاولة"""
    if not DATABASE_URL:
        logger.error("DATABASE_URL missing in environment variables!")
        raise ValueError("DATABASE_URL is not set")
        
    parsed_url = urlparse(DATABASE_URL.strip())
    
    username = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else 5432
    dbname = parsed_url.path.lstrip('/')

    # محاولة الاتصال 5 مرات متتالية لإيقاظ السيرفر الخامل
    for attempt in range(5):
        try:
            return pg8000.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=dbname,
                ssl_context=True
            )
        except Exception as e:
            if attempt == 4:
                logger.error(f"❌ فشلت كافة محاولات الاتصال بقاعدة البيانات: {e}")
                raise e
            logger.warning(f"🔄 محاولة الاتصال بقاعدة البيانات فشلت ({attempt + 1}/5)، جاري إعادة المحاولة خلال ثانيتين...")
            time.sleep(2)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. إنشاء جدول البوتات الأساسي
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bots (
            user_id BIGINT PRIMARY KEY,
            token TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 0,
            expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days',
            is_banned INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

    # فحص وإضافة الأعمدة الناقصة بطريقة احترافية
    def column_exists(table, column):
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}' AND column_name='{column}'")
        return cursor.fetchone()[0] > 0

    if not column_exists('user_bots', 'expires_at'):
        cursor.execute("ALTER TABLE user_bots ADD COLUMN expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days'")
        conn.commit()

    if not column_exists('user_bots', 'is_banned'):
        cursor.execute("ALTER TABLE user_bots ADD COLUMN is_banned INTEGER DEFAULT 0")
        conn.commit()

    # 2. إنشاء جدول ربط الحسابات لموقع DurianRCS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_site_accounts (
            user_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            api_key TEXT NOT NULL
        )
    ''')
    conn.commit()

    # 3. إنشاء جدول قنوات الصيد الجديدة تلقائياً
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_hunting_channels (
            user_id BIGINT PRIMARY KEY,
            channel_id TEXT NOT NULL
        )
    ''')
    conn.commit()

    # 4. إنشاء جدول تتبع حالة تشغيل الصيد الفعلي للمستخدم
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_hunting_status (
            user_id BIGINT PRIMARY KEY,
            is_hunting INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

    # 5. إنشاء جدول الدول المراد الصيد منها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_countries (
            user_id BIGINT,
            country_name TEXT,
            PRIMARY KEY (user_id, country_name)
        )
    ''')
    conn.commit()
    
    # 6. حسابات Telegram المستخدمة لفحص الأرقام
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_accounts (
            id SERIAL PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            api_id INTEGER NOT NULL,
            api_hash TEXT NOT NULL,
            string_session TEXT NOT NULL,
            status INTEGER DEFAULT 1,
            flood_until TIMESTAMP NULL,
            total_checks INTEGER DEFAULT 0,
            last_used TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    conn.commit()
    
    if not column_exists('telegram_accounts', 'is_active'):
        cursor.execute("ALTER TABLE telegram_accounts ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
        conn.commit()

    if not column_exists('telegram_accounts', 'session'):
        cursor.execute("ALTER TABLE telegram_accounts ADD COLUMN session TEXT")
        conn.commit()
 
    cursor.close()
    conn.close()

def save_bot(user_id, token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_bots (user_id, token, is_active, expires_at, is_banned) 
        VALUES (%s, %s, 0, CURRENT_TIMESTAMP + INTERVAL '30 days', 0)
        ON CONFLICT (user_id) 
        DO UPDATE SET token = EXCLUDED.token;
    ''', (user_id, token))
    conn.commit()
    cursor.close()
    conn.close()

def add_days_to_user(user_id, days):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_bots 
        SET expires_at = GREATEST(expires_at, CURRENT_TIMESTAMP) + CAST(%s AS INTERVAL)
        WHERE user_id = %s
    ''', (f"{days} days", user_id))
    conn.commit()
    cursor.close()
    conn.close()

def ban_user(user_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE user_bots SET is_banned = %s WHERE user_id = %s', (status, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_status(user_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE user_bots SET is_active = %s WHERE user_id = %s', (is_active, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_bot(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT token, is_active, expires_at, is_banned FROM user_bots WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Exception:
        cursor.close()
        conn.close()
        return None

def get_all_active_bots():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id, token FROM user_bots WHERE is_active = 1 AND is_banned = 0')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception:
        cursor.close()
        conn.close()
        return []

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM user_bots')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM user_bots WHERE is_active = 1')
        active = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total if total else 0, active if active else 0
    except Exception:
        cursor.close()
        conn.close()
        return 0, 0

def save_site_account(user_id, username, api_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_site_accounts (user_id, username, api_key)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET username = EXCLUDED.username, api_key = EXCLUDED.api_key;
    ''', (user_id, username, api_key))
    conn.commit()
    cursor.close()
    conn.close()

def get_site_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT username, api_key FROM user_site_accounts WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row
    except Exception:
        cursor.close()
        conn.close()
        return None

def save_hunting_channel(user_id, channel_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_hunting_channels (user_id, channel_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET channel_id = EXCLUDED.channel_id;
    ''', (user_id, str(channel_id)))
    conn.commit()
    cursor.close()
    conn.close()

def get_hunting_channel(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT channel_id FROM user_hunting_channels WHERE user_id = %s',
            (user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()

def set_hunting_status(user_id, is_hunting):
    status_val = 1 if is_hunting else 0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_hunting_status (user_id, is_hunting)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET is_hunting = EXCLUDED.is_hunting
    ''', (user_id, status_val))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_countries(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT country_name FROM user_countries WHERE user_id = %s',
            (user_id,)
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    finally:
        cursor.close()
        conn.close()

def add_user_country(user_id, country_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_countries (user_id, country_name)
            VALUES (%s, %s)
            ON CONFLICT (user_id, country_name) DO NOTHING
        ''', (user_id, country_name))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def save_telegram_account(phone, api_id, api_hash, string_session):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO telegram_accounts
        (phone, api_id, api_hash, string_session)

        VALUES (%s,%s,%s,%s)

        ON CONFLICT (phone)

        DO UPDATE SET

        api_id=EXCLUDED.api_id,

        api_hash=EXCLUDED.api_hash,

        string_session=EXCLUDED.string_session,

        status=1
    """,(phone, api_id, api_hash, string_session))

    conn.commit()

    cursor.close()

    conn.close()

def get_telegram_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
        id,
        phone,
        api_id,
        api_hash,
        string_session,
        status,
        flood_until,
        total_checks,
        last_used

        FROM telegram_accounts

        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

def delete_telegram_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM telegram_accounts WHERE id=%s",
        (account_id,)
    )

    conn.commit()

    cursor.close()

    conn.close()

def set_account_flood(account_id, flood_until):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    UPDATE telegram_accounts

    SET flood_until=%s

    WHERE id=%s

    """,(flood_until, account_id))

    conn.commit()

    cursor.close()

    conn.close()

def increase_account_checks(account_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    UPDATE telegram_accounts

    SET

    total_checks=total_checks+1,

    last_used=CURRENT_TIMESTAMP

    WHERE id=%s

    """,(account_id,))

    conn.commit()

    cursor.close()

    conn.close()

def get_best_telegram_account():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT

    id,

    phone,

    api_id,

    api_hash,

    string_session

    FROM telegram_accounts

    WHERE

    status=1

    AND

    (

    flood_until IS NULL

    OR

    flood_until<CURRENT_TIMESTAMP

    )

    ORDER BY

    total_checks ASC,

    last_used ASC NULLS FIRST

    LIMIT 1

    """)

    row = cursor.fetchone()

    cursor.close()

    conn.close()

    return row
