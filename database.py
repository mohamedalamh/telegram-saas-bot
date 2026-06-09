import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# USERS
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    created_at TEXT
)
""")

# TOKENS + API SETTINGS
cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    user_id INTEGER PRIMARY KEY,
    token TEXT,
    api_user TEXT,
    api_key TEXT,
    project_id TEXT,
    channel_id TEXT,
    status TEXT,
    subscription_end TEXT
)
""")

conn.commit()


# ---------------- USERS ----------------
def add_user(user_id, username):
    cur.execute("""
        INSERT OR IGNORE INTO users VALUES (?,?,?)
    """, (user_id, username, str(datetime.utcnow())))
    conn.commit()


# ---------------- ACCOUNT ----------------
def save_account(user_id, token=None, api_user=None, api_key=None, project_id=None, channel_id=None):
    cur.execute("""
        INSERT INTO accounts (user_id, token, api_user, api_key, project_id, channel_id, status, subscription_end)
        VALUES (?, ?, ?, ?, ?, ?, 'inactive', '')
        ON CONFLICT(user_id) DO UPDATE SET
            token=COALESCE(?, token),
            api_user=COALESCE(?, api_user),
            api_key=COALESCE(?, api_key),
            project_id=COALESCE(?, project_id),
            channel_id=COALESCE(?, channel_id)
    """, (
        user_id,
        token, api_user, api_key, project_id, channel_id,
        token, api_user, api_key, project_id, channel_id
    ))
    conn.commit()


def get_account(user_id):
    cur.execute("SELECT * FROM accounts WHERE user_id=?", (user_id,))
    return cur.fetchone()


def set_status(user_id, status):
    cur.execute("UPDATE accounts SET status=? WHERE user_id=?", (status, user_id))
    conn.commit()


def set_subscription(user_id, days):
    end = datetime.utcnow() + timedelta(days=days)
    cur.execute("UPDATE accounts SET subscription_end=? WHERE user_id=?", (str(end), user_id))
    conn.commit()
