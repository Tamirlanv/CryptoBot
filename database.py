import sqlite3

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coingecko (
            user_id INTEGER PRIMARY KEY,
            api_key TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            coin TEXT NOT NULL,
            direction TEXT NOT NULL,    -- 'above' or 'below'
            threshold REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'usd',
            triggered INTEGER NOT NULL DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()
    
def save_cg_key(user_id, api_key):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO coingecko (user_id, api_key)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET api_key = excluded.api_key;
    """, (user_id, api_key))
    conn.commit()
    conn.close()

def get_cg_key(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT api_key FROM coingecko WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# -------- Alerts ----------
def add_alert_db(user_id, coin, direction, threshold, currency="usd"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (user_id, coin, direction, threshold, currency)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, coin, direction, threshold, currency))
    conn.commit()
    alert_id = cur.lastrowid
    conn.close()
    return alert_id

def list_alerts_db(user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT id, coin, direction, threshold, currency, triggered FROM alerts WHERE user_id=?", (user_id,))
    else:
        cur.execute("SELECT id, user_id, coin, direction, threshold, currency, triggered FROM alerts")
    rows = cur.fetchall()
    conn.close()
    return rows

def remove_alert_db(alert_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()

def set_alert_triggered(alert_id, triggered: bool):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE alerts SET triggered=? WHERE id=?", (1 if triggered else 0, alert_id))
    conn.commit()
    conn.close()