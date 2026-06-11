import os
import pg8000

# قراءة رابط الاتصال من متغيرات بيئة Railway
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """تحليل الرابط واستخراج بيانات الاتصال المتوافقة مع pg8000 بشكل آمن"""
    url = DATABASE_URL.strip()
    
    # فصل البارامترات الإضافية مثل ?sslmode=require عن مسار البيانات الرئيسي
    if "?" in url:
        url = url.split("?")[0]
        
    # تفكيك الرابط المستخرج من Neon ليتناسب مع بارامترات pg8000
    url = url.replace("postgres://", "").replace("postgresql://", "")
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, dbname = host_db.split("/")
    
    # حل مشكلة الـ Port إذا وجد أو وضع الافتراضي
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432

    # الاتصال الآمن والمباشر بالقاعدة
    return pg8000.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=dbname,
        ssl_context=True # تفعيل الأمان المشفر المطلوب في منصة Neon
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
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
