import sqlite3

DB_NAME = "data.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect()
    cur = conn.cursor()

    # المستخدمين + الاشتراك
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        subscription_end TEXT DEFAULT NULL
    )
    """)

    # البوتات التابعة للمستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bot_token TEXT,
        status TEXT DEFAULT 'stopped'
    )
    """)

    # إعدادات كل مستخدم
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_id TEXT,
        api_name TEXT,
        api_key TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, username)
    VALUES (?, ?)
    """, (user_id, username))

    conn.commit()
    conn.close()


def save_bot(user_id, token):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO user_bots (user_id, bot_token, status)
    VALUES (?, ?, 'stopped')
    """, (user_id, token))

    conn.commit()
    conn.close()


def get_user_bots(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM user_bots WHERE user_id=?", (user_id,))
    data = cur.fetchall()

    conn.close()
    return data
