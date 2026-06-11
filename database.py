import os
import psycopg2

# قراءة رابط الاتصال تلقائياً من نظام تشغيل Railway
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # استخدام BIGINT لأن معرفات تيليجرام أصبحت أرقاماً ضخمة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bots (
            user_id BIGINT PRIMARY KEY,
            token TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_bot(user_id, token):
    conn = get_connection()
    cursor = conn.cursor()
    # استعلام ذكي: إذا كان المستخدم مسجلاً مسبقاً يقوم بتحديث التوكن فقط
    cursor.execute('''
        INSERT INTO user_bots (user_id, token, is_active) 
        VALUES (%s, %s, 0)
        ON CONFLICT (user_id) 
        DO UPDATE SET token = EXCLUDED.token;
    ''', (user_id, token))
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
    cursor.execute('SELECT token, is_active FROM user_bots WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_all_active_bots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, token FROM user_bots WHERE is_active = 1')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
