import sqlite3

DB = "bot.db"


def connect():
    return sqlite3.connect(DB)


# ---------------- INIT DB ----------------
def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        token TEXT,
        api_name TEXT,
        api_key TEXT,
        channel_id TEXT,
        country TEXT,
        status TEXT DEFAULT 'inactive'
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USER ----------------
def add_user(user_id, username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, username)
    VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row


# ---------------- TOKEN ----------------
def save_token(user_id, token):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET token=? WHERE user_id=?
    """, (token, user_id))

    conn.commit()
    conn.close()


def get_token(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT token FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


# ---------------- STATUS ----------------
def set_status(user_id, status):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET status=? WHERE user_id=?
    """, (status, user_id))

    conn.commit()
    conn.close()
