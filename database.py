import sqlite3

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        bot_token TEXT,
        active INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def save_token(user_id, token):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO users
    (user_id, bot_token, active)
    VALUES (?, ?, 0)
    """, (user_id, token))

    conn.commit()
    conn.close()


def get_token(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT bot_token FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


def set_active(user_id, value):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET active=? WHERE user_id=?",
        (value, user_id)
    )

    conn.commit()
    conn.close()


def is_active(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT active FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()
    conn.close()

    return row[0] if row else 0
