import sqlite3

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        token TEXT,
        status INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def save_token(user_id, token):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO users
    (user_id, token, status)
    VALUES (
        ?,
        ?,
        COALESCE(
            (SELECT status FROM users WHERE user_id=?),
            0
        )
    )
    """, (user_id, token, user_id))

    conn.commit()
    conn.close()


def get_token(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT token FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None


def set_status(user_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET status=? WHERE user_id=?",
        (status, user_id)
    )

    conn.commit()
    conn.close()


def get_status(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT status FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else 0
