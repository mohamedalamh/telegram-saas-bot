import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    token TEXT,
    status TEXT
)
""")

conn.commit()


def save_token(user_id, token):
    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, token, status)
    VALUES (?, ?, ?)
    """, (user_id, token, "stopped"))
    conn.commit()


def get_token(user_id):
    row = cursor.execute(
        "SELECT token FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()
    return row[0] if row else None


def set_status(user_id, status):
    cursor.execute(
        "UPDATE users SET status=? WHERE user_id=?",
        (status, user_id)
    )
    conn.commit()


def get_status(user_id):
    row = cursor.execute(
        "SELECT status FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()
    return row[0] if row else "stopped"
