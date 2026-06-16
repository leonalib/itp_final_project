import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", 8419513332))]

DB_NAME = os.environ.get("DB_NAME", "Cake_Helper")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("PGPASSWORD")
DB_HOST = os.environ.get("PGHOST")