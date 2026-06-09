import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# 🔥 إنشاء كل الجداول عند التشغيل
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tokens (
    user_id INTEGER PRIMARY KEY,
    token TEXT
)
""")

conn.commit()


# ---------------- USERS ----------------
def add_user(user_id, username):
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?)",
        (user_id, username)
    )
    conn.commit()


# ---------------- TOKENS ----------------
def save_token(user_id, token):
    cur.execute(
        "INSERT OR REPLACE INTO tokens VALUES (?,?)",
        (user_id, token)
    )
    conn.commit()


def get_token(user_id):
    cur.execute(
        "SELECT token FROM tokens WHERE user_id=?",
        (user_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None
