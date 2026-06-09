import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    token TEXT,
    country TEXT,
    status TEXT DEFAULT 'inactive',
    plan TEXT DEFAULT 'free'
)
""")

conn.commit()

# ➕ إضافة مستخدم
def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

# 👤 جلب مستخدم
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# 🔑 تحديث التوكن
def update_token(user_id, token):
    cursor.execute("UPDATE users SET token=? WHERE user_id=?", (token, user_id))
    conn.commit()

# ▶️ تشغيل/إيقاف
def update_status(user_id, status):
    cursor.execute("UPDATE users SET status=? WHERE user_id=?", (status, user_id))
    conn.commit()

# 💳 تغيير الخطة
def update_plan(user_id, plan):
    cursor.execute("UPDATE users SET plan=? WHERE user_id=?", (plan, user_id))
    conn.commit()

# 👥 كل المستخدمين
def get_all_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
