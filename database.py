import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        client_encoding="UTF8"
    )

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id         SERIAL PRIMARY KEY,
            chat_id    BIGINT,
            username   TEXT,
            flavor     TEXT,
            size       TEXT,
            photo_id   TEXT,
            extras     TEXT,
            status     TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'new'
    """)

    conn.commit()
    conn.close()


def save_order(chat_id, username, flavor, size, photo_id, extras):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO orders (chat_id, username, flavor, size, photo_id, extras, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'new')
            RETURNING id
        """, (chat_id, username, flavor, size, photo_id, extras))
        order_id = cur.fetchone()[0]
        conn.commit()
        return order_id        
    except Exception as e:
        conn.rollback()
        print(f"DB Error (save_order): {e}")
        return None            
    finally:
        conn.close()


def get_orders(status_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    if status_filter:
        cur.execute("SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at FROM orders WHERE status = %s ORDER BY created_at DESC", (status_filter,))
    else:
        cur.execute("SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_order_by_id(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_order_status(order_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s RETURNING chat_id, flavor", (new_status, order_id))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result

def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'new'),
            COUNT(*) FILTER (WHERE status = 'in_progress'),
            COUNT(*) FILTER (WHERE status = 'ready'),
            COUNT(*) FILTER (WHERE status = 'delivered'),
            COUNT(*) FILTER (WHERE status = 'cancelled'),
            COUNT(*)
        FROM orders
    """)
    counts = cur.fetchone()
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days'),
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days')
        FROM orders
    """)
    periods = cur.fetchone()
    conn.close()
    return counts, periods