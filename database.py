import os
import pg8000

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    url = DATABASE_URL.strip()
    if "?" in url:
        url = url.split("?")[0]
        
    url = url.replace("postgres://", "").replace("postgresql://", "")
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, dbname = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432

    return pg8000.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=dbname,
        ssl_context=True
    )

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

    try:
        cursor.execute("ALTER TABLE user_bots ADD COLUMN expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days'")
        conn.commit()
    except Exception:
        conn.rollback()

    try:
        cursor.execute("ALTER TABLE user_bots ADD COLUMN is_banned INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        conn.rollback()

    # 2. إنشاء جدول ربط الحسابات لموقع DurianRCS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_site_accounts (
            user_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            api_key TEXT NOT NULL
        )
    ''')
    conn.commit()

    # 3. إنشاء جدول قنوات الصيد
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_hunting_channels (
            user_id BIGINT PRIMARY KEY,
            channel_id TEXT NOT NULL
        )
    ''')
    conn.commit()

    # 🔥 4. إضافة جدول الدول المفعلة لكل مستخدم (مهم جداً لربط الصيد)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_countries (
            user_id BIGINT,
            country_name TEXT,
            PRIMARY KEY (user_id, country_name)
        )
    ''')
    conn.commit()

    # 🔥 5. إضافة عمود حالة الصيد الحالي في جدول الحسابات لتتبع التشغيل والإيقاف
    try:
        cursor.execute("ALTER TABLE user_site_accounts ADD COLUMN is_hunting INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        conn.rollback()

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
        total = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM user_bots WHERE is_active = 1')
        active = cursor.fetchone()
        cursor.close()
        conn.close()
        return total[0] if total else 0, active[0] if active else 0
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
    cursor = cursor = conn.cursor()
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
        cursor.execute('SELECT channel_id FROM user_hunting_channels WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None
    except Exception:
        cursor.close()
        conn.close()
        return None

# 🔥 الدوال الجديدة المضافة لضمان ربط الدول وتشغيل وإيقاف الصيد تلقائياً:

def set_hunting_status(user_id, is_hunting):
    """تحديث حالة تشغيل الصيد الفعلي للمستخدم في قاعدة البيانات"""
    status_val = 1 if is_hunting else 0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE user_site_accounts SET is_hunting = %s WHERE user_id = %s', (status_val, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_countries(user_id):
    """جلب قائمة الدول المضافة والمفعلة لصيد هذا المستخدم"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT country_name FROM user_countries WHERE user_id = %s', (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception:
        cursor.close()
        conn.close()
        return []

def add_user_country(user_id, country_name):
    """إضافة دولة جديدة لقائمة الصيد الخاصة بالمستخدم"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_countries (user_id, country_name)
            VALUES (%s, %s)
            ON CONFLICT (user_id, country_name) DO NOTHING;
        ''', (user_id, country_name))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
