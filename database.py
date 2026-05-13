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

    # Main orders table
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

    # Add status column if the table already existed without it
    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'new'
    """)

    conn.commit()
    conn.close()


# ── Client writes ─────────────────────────────────────────────

def save_order(chat_id, username, flavor, size, photo_id, extras):
    """Insert a new order and return its id, or None on failure."""
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
        return order_id          # truthy on success
    except Exception as e:
        conn.rollback()
        print(f"DB Error (save_order): {e}")
        return None              # falsy on failure
    finally:
        conn.close()


# ── Admin reads ───────────────────────────────────────────────

def get_orders(status_filter=None, limit=20):
    """Return a list of orders, optionally filtered by status."""
    conn = get_connection()
    cur = conn.cursor()
    if status_filter:
        cur.execute("""
            SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at
            FROM orders
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (status_filter, limit))
    else:
        cur.execute("""
            SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at
            FROM orders
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_order_by_id(order_id):
    """Return a single order row or None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, chat_id, username, flavor, size, photo_id, extras, status, created_at
        FROM orders
        WHERE id = %s
    """, (order_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_order_status(order_id, new_status):
    """Update status and return (chat_id, flavor) for customer notification."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE orders SET status = %s WHERE id = %s
            RETURNING chat_id, flavor
        """, (new_status, order_id))
        result = cur.fetchone()
        conn.commit()
        return result            # (chat_id, flavor) or None
    except Exception as e:
        conn.rollback()
        print(f"DB Error (update_status): {e}")
        return None
    finally:
        conn.close()


def get_stats():
    """Return order counts by status plus weekly/monthly totals."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'new')         AS new_count,
            COUNT(*) FILTER (WHERE status = 'in_progress') AS in_progress,
            COUNT(*) FILTER (WHERE status = 'ready')       AS ready,
            COUNT(*) FILTER (WHERE status = 'delivered')   AS delivered,
            COUNT(*) FILTER (WHERE status = 'cancelled')   AS cancelled,
            COUNT(*)                                        AS total
        FROM orders
    """)
    counts = cur.fetchone()

    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days')  AS week,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS month
        FROM orders
        WHERE status != 'cancelled'
    """)
    periods = cur.fetchone()
    conn.close()
    return counts, periods