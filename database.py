"""
database.py — PostgreSQL persistence layer for Cake Bot.

Works alongside models.py: converts between CakeOrder objects
and raw DB rows, and integrates with OrderRepository for file export.
"""

import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
from models import CakeOrder, CustomOrder, OrderRepository


# ─────────────────────────────────────────────
#  Connection helper
# ─────────────────────────────────────────────
def get_connection():
    """Return a new psycopg2 connection. Raises on failure."""
    return psycopg2.connect(
        dbname="Cake_Helper",
        user="postgres",
        password="1234",
        host="localhost",
        client_encoding="UTF8"
    )


# ─────────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────────
def create_table():
    """Create the orders table if it doesn't exist."""
    conn = get_connection()
    try:
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
    except Exception as e:
        conn.rollback()
        print(f"[DB] create_table error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  CRUD helpers (used by handlers & admin)
# ─────────────────────────────────────────────
def save_order(chat_id, username, flavor, size, photo_id, extras):
    """
    Insert a new order into the DB.

    Also:
      - Decides if this is a CustomOrder (both flavor & size are free-text)
        and stores it in orders_backup.json via OrderRepository.
      - Returns the new order id (int) on success, or None on failure.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (chat_id, username, flavor, size, photo_id, extras, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'new')
            RETURNING id
        """, (chat_id, username, flavor, size, photo_id, extras))
        order_id = cur.fetchone()[0]
        conn.commit()

        # ── OOP: build the correct model object & persist to JSON ──
        is_custom = flavor.lower().startswith("custom") or size.lower().startswith("custom")
        if is_custom:
            order_obj = CustomOrder(
                chat_id=chat_id, username=username,
                flavor=flavor, size=size, photo_id=photo_id, extras=extras,
            )
        else:
            order_obj = CakeOrder(
                chat_id=chat_id, username=username,
                flavor=flavor, size=size, photo_id=photo_id, extras=extras,
            )
        order_obj.order_id = order_id

        repo = OrderRepository()
        existing = repo.load_from_json()
        existing.append(order_obj)
        repo.save_to_json(existing)          # Data persistence: JSON write
        repo.export_to_csv(existing)         # Data persistence: CSV export

        return order_id

    except Exception as e:
        conn.rollback()
        print(f"[DB] save_order error: {e}")
        return None
    finally:
        conn.close()


def get_orders(status_filter=None):
    """Fetch orders from DB, optionally filtered by status."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        if status_filter:
            cur.execute("""
                SELECT id, chat_id, username, flavor, size,
                       photo_id, extras, status, created_at
                FROM orders WHERE status = %s
                ORDER BY created_at DESC
            """, (status_filter,))
        else:
            cur.execute("""
                SELECT id, chat_id, username, flavor, size,
                       photo_id, extras, status, created_at
                FROM orders ORDER BY created_at DESC
            """)
        return cur.fetchall()
    except Exception as e:
        print(f"[DB] get_orders error: {e}")
        return []
    finally:
        conn.close()


def get_order_by_id(order_id):
    """Fetch a single order row by id."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, chat_id, username, flavor, size,
                   photo_id, extras, status, created_at
            FROM orders WHERE id = %s
        """, (order_id,))
        return cur.fetchone()
    except Exception as e:
        print(f"[DB] get_order_by_id error: {e}")
        return None
    finally:
        conn.close()


def update_order_status(order_id, new_status):
    """
    Update order status in DB.

    Also updates the local JSON backup via OrderRepository.
    Returns (chat_id, flavor) tuple on success, or None on failure.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE orders SET status = %s
            WHERE id = %s
            RETURNING chat_id, flavor
        """, (new_status, order_id))
        result = cur.fetchone()
        conn.commit()

        # ── keep JSON backup in sync ──
        if result:
            repo = OrderRepository()
            orders = repo.load_from_json()
            for o in orders:
                if o.order_id == order_id:
                    o.status = new_status
                    break
            repo.save_to_json(orders)
            repo.export_to_csv(orders)

        return result
    except Exception as e:
        conn.rollback()
        print(f"[DB] update_order_status error: {e}")
        return None
    finally:
        conn.close()


def get_stats():
    """Return (counts_tuple, periods_tuple) with aggregated order statistics."""
    conn = get_connection()
    try:
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
        return counts, periods
    except Exception as e:
        print(f"[DB] get_stats error: {e}")
        return (0, 0, 0, 0, 0, 0), (0, 0)
    finally:
        conn.close()