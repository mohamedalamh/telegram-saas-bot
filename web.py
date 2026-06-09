from fastapi import FastAPI
import sqlite3
from fastapi.responses import HTMLResponse

app = FastAPI()

conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

# ================= DASHBOARD =================
@app.get("/", response_class=HTMLResponse)
def dashboard():

    cursor.execute("SELECT user_id, bot_token, api, status, subscription FROM users")
    users = cursor.fetchall()

    html = """
    <html>
    <head>
        <title>SaaS Dashboard</title>
        <style>
            body { font-family: Arial; background:#111; color:white; padding:20px }
            table { width:100%; border-collapse: collapse; }
            th, td { padding:10px; border:1px solid #444; text-align:center }
            th { background:#222 }
        </style>
    </head>
    <body>
        <h1>👑 SaaS Control Panel</h1>
        <table>
            <tr>
                <th>User ID</th>
                <th>Token</th>
                <th>API</th>
                <th>Status</th>
                <th>Subscription</th>
            </tr>
    """

    for u in users:
        html += f"""
        <tr>
            <td>{u[0]}</td>
            <td>{"✔" if u[1] else "❌"}</td>
            <td>{"✔" if u[2] else "❌"}</td>
            <td>{u[3]}</td>
            <td>{u[4]}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html
