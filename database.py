import sqlite3

DB_NAME = "saas_bots.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bots (
            user_id INTEGER PRIMARY KEY,
            token TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_bot(user_id, token):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_bots (user_id, token, is_active) 
        VALUES (?, ?, (SELECT is_active FROM user_bots WHERE user_id = ?))
    ''', (user_id, token, user_id))
    conn.commit()
    conn.close()

def set_bot_status(user_id, is_active):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_bots SET is_active = ? WHERE user_id = ?', (is_active, user_id))
    conn.commit()
    conn.close()

def get_bot(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT token, is_active FROM user_bots WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_active_bots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, token FROM user_bots WHERE is_active = 1')
    rows = cursor.fetchall()
    conn.close()
    return rows
