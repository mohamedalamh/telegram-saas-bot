from fastapi import FastAPI
import sqlite3

app = FastAPI()

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

@app.get("/users")
def users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

@app.get("/status/{user_id}")
def status(user_id: int):
    cursor.execute("SELECT status FROM users WHERE user_id=?", (user_id,))
    return {"status": cursor.fetchone()}
