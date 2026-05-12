import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

def get_connection():
    return psycopg2.connect(
        dbname="Cake_Helper",
        user="postgres",
        password="1234",
        host="localhost",
        client_encoding="UTF8"
    )

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT,
        username TEXT,
        flavor TEXT,
        size TEXT,
        photo_id TEXT,
        extras TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
    conn.commit()
    conn.close()

def save_order(chat_id, username, flavor, size, photo_id, extras):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO orders (chat_id, username, flavor, size, photo_id, extras)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (chat_id, username, flavor, size, photo_id, extras))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"DB Error: {e}")
        return False
    finally:
        conn.close()