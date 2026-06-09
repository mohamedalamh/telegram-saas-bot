import sqlite3

DB_NAME = "bot.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # جدول المستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        token TEXT DEFAULT NULL,
        status TEXT DEFAULT 'inactive'
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, username)
    VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()


def save_token(user_id, token):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET token=? WHERE user_id=?
    """, (token, user_id))

    conn.commit()
    conn.close()


def get_token(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT token FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()

    return row[0] if row else None


def set_status(user_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET status=? WHERE user_id=?
    """, (status, user_id))

    conn.commit()
    conn.close()
