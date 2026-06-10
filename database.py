import sqlite3

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        token TEXT,
        status TEXT DEFAULT 'stopped'
    )
    """)

    conn.commit()
    conn.close()


def set_token(user_id, token):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT OR REPLACE INTO users (user_id, token, status)
    VALUES (?, ?, COALESCE((SELECT status FROM users WHERE user_id=?), 'stopped'))
    """, (user_id, token, user_id))

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT user_id, token, status FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()

    conn.close()
    return row


def set_status(user_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("UPDATE users SET status=? WHERE user_id=?", (status, user_id))

    conn.commit()
    conn.close()
