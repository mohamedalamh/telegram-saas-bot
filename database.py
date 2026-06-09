import sqlite3

DB = "bot.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # المستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        token TEXT,
        api_name TEXT,
        api_key TEXT,
        channel_id TEXT,
        country TEXT,
        status TEXT DEFAULT 'inactive',
        subscription_end INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, username)
    VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()


def update_token(user_id, token):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("UPDATE users SET token=? WHERE user_id=?", (token, user_id))
    conn.commit()
    conn.close()


def update_api(user_id, name, key):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET api_name=?, api_key=? WHERE user_id=?
    """, (name, key, user_id))

    conn.commit()
    conn.close()


def update_channel(user_id, channel_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET channel_id=? WHERE user_id=?
    """, (channel_id, user_id))

    conn.commit()
    conn.close()


def update_country(user_id, country):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users SET country=? WHERE user_id=?
    """, (country, user_id))

    conn.commit()
    conn.close()


def set_status(user_id, status):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("UPDATE users SET status=? WHERE user_id=?", (status, user_id))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row
