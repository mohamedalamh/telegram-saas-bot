import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    token TEXT,
    active INTEGER DEFAULT 0
)
""")

conn.commit()


def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, token, active) VALUES (?, '', 0)", (user_id,))
    conn.commit()


def set_token(user_id, token):
    cursor.execute("UPDATE users SET token=? WHERE user_id=?", (token, user_id))
    conn.commit()


def set_active(user_id, status):
    cursor.execute("UPDATE users SET active=? WHERE user_id=?", (status, user_id))
    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def get_all_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
