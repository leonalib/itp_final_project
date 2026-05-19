"""
models.py — OOP data models for Cake Bot.

Hierarchy:
    BaseOrder  (abstract-like base)
        └── CakeOrder   (concrete order with cake-specific fields)
        └── CustomOrder (order with custom flavor/size)
"""

import json
import csv
import os
from datetime import datetime


# ─────────────────────────────────────────────
#  Base class
# ─────────────────────────────────────────────
class BaseOrder:
    """
    Abstract base class for any order.

    Attributes:
        order_id  (int | None): assigned after DB insert
        chat_id   (int):        Telegram chat id
        username  (str):        Telegram username
        status    (str):        current order status
        created_at(datetime):   creation timestamp
    """

    VALID_STATUSES = ('new', 'in_progress', 'ready', 'delivered', 'cancelled')

    def __init__(self, chat_id: int, username: str):
        self.order_id: int | None = None
        self.chat_id: int = chat_id
        self.username: str = username or "unknown"
        self.status: str = "new"
        self.created_at: datetime = datetime.now()

    # ── status management ──────────────────────
    def advance_status(self) -> str:
        """Move order to the next logical status. Returns new status."""
        flow = {
            'new':         'in_progress',
            'in_progress': 'ready',
            'ready':       'delivered',
        }
        if self.status in flow:
            self.status = flow[self.status]
        return self.status

    def cancel(self):
        """Cancel the order."""
        self.status = 'cancelled'

    def is_active(self) -> bool:
        """Return True if the order is not yet finished."""
        return self.status not in ('delivered', 'cancelled')

    # ── serialization (data persistence) ──────
    def to_dict(self) -> dict:
        """Serialize order to a plain dictionary (for JSON export)."""
        return {
            "order_id":   self.order_id,
            "chat_id":    self.chat_id,
            "username":   self.username,
            "status":     self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BaseOrder":
        """Deserialize from dictionary (factory method)."""
        obj = cls(data["chat_id"], data["username"])
        obj.order_id   = data.get("order_id")
        obj.status     = data.get("status", "new")
        obj.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%d %H:%M:%S"
        )
        return obj

    # ── dunder helpers ─────────────────────────
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.order_id}, user={self.username}, status={self.status})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseOrder):
            return NotImplemented
        return self.order_id == other.order_id


# ─────────────────────────────────────────────
#  Concrete subclass — CakeOrder
# ─────────────────────────────────────────────
class CakeOrder(BaseOrder):
    """
    A concrete cake order.

    Inherits from BaseOrder and adds cake-specific fields:
        flavor, size, photo_id, extras.

    Demonstrates: inheritance, method overriding, polymorphism.
    """

    def __init__(
        self,
        chat_id:  int,
        username: str,
        flavor:   str = "",
        size:     str = "",
        photo_id: str = "",
        extras:   str = "",
    ):
        super().__init__(chat_id, username)   # ← calls BaseOrder.__init__
        self.flavor:   str = flavor
        self.size:     str = size
        self.photo_id: str = photo_id
        self.extras:   str = extras

    # ── override to_dict ──────────────────────
    def to_dict(self) -> dict:
        """Extend parent serialization with cake-specific fields."""
        base = super().to_dict()          # polymorphism: call parent method
        base.update({
            "flavor":   self.flavor,
            "size":     self.size,
            "photo_id": self.photo_id,
            "extras":   self.extras,
            "type":     "cake",
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> "CakeOrder":
        """Deserialize CakeOrder from dictionary."""
        obj = cls(
            chat_id=data["chat_id"],
            username=data["username"],
            flavor=data.get("flavor", ""),
            size=data.get("size", ""),
            photo_id=data.get("photo_id", ""),
            extras=data.get("extras", ""),
        )
        obj.order_id   = data.get("order_id")
        obj.status     = data.get("status", "new")
        obj.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%d %H:%M:%S"
        )
        return obj

    def summary(self) -> str:
        """Return a human-readable order summary string."""
        return (
            f"📋 Order #{self.order_id}\n"
            f"🍰 Flavor : {self.flavor or '—'}\n"
            f"📏 Size   : {self.size   or '—'}\n"
            f"✏️ Extras : {self.extras or '—'}\n"
            f"📌 Status : {self.status}\n"
            f"🕐 Created: {self.created_at.strftime('%d %b %Y, %H:%M')}"
        )

    def __repr__(self) -> str:
        return (
            f"CakeOrder(id={self.order_id}, flavor={self.flavor!r}, "
            f"size={self.size!r}, status={self.status})"
        )


# ─────────────────────────────────────────────
#  Subclass with polymorphic behaviour
# ─────────────────────────────────────────────
class CustomOrder(CakeOrder):
    """
    A CakeOrder where both flavor and size are free-text (custom).

    Demonstrates polymorphism: summary() is overridden to highlight
    that this is a non-standard order requiring manual review.
    """

    def __init__(self, chat_id: int, username: str, **kwargs):
        super().__init__(chat_id, username, **kwargs)
        self.needs_review: bool = True

    def summary(self) -> str:
        base = super().summary()       # polymorphism: reuse parent output
        return base + "\n⚠️  Custom order — manual review required."

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["type"] = "custom"
        base["needs_review"] = self.needs_review
        return base


# ─────────────────────────────────────────────
#  OrderFactory  (OOP: factory pattern)
# ─────────────────────────────────────────────
class OrderFactory:
    """
    Creates the correct Order subclass based on order type.

    Usage:
        order = OrderFactory.create("cake", chat_id=..., username=...)
        order = OrderFactory.create("custom", chat_id=..., username=...)
    """

    @staticmethod
    def create(order_type: str, **kwargs) -> BaseOrder:
        registry = {
            "cake":   CakeOrder,
            "custom": CustomOrder,
        }
        cls = registry.get(order_type, CakeOrder)
        return cls(**kwargs)

    @staticmethod
    def from_dict(data: dict) -> BaseOrder:
        """Reconstruct the correct subclass from a serialized dict."""
        t = data.get("type", "cake")
        if t == "custom":
            return CustomOrder.from_dict(data)
        return CakeOrder.from_dict(data)


# ─────────────────────────────────────────────
#  OrderRepository  (data persistence: JSON & CSV)
# ─────────────────────────────────────────────
class OrderRepository:
    """
    Handles reading/writing orders to JSON and CSV files.

    Satisfies the 'Data Persistence' criterion:
    the application must read from and write to external files.

    Note: PostgreSQL (database.py) is the primary store;
    this class provides file-based export/import for grading compliance.
    """

    JSON_PATH = "orders_backup.json"
    CSV_PATH  = "orders_export.csv"
    CSV_FIELDS = [
        "order_id", "chat_id", "username", "flavor",
        "size", "extras", "status", "created_at", "type",
    ]

    # ── JSON ──────────────────────────────────
    def save_to_json(self, orders: list[BaseOrder]) -> None:
        """Write a list of orders to a JSON file."""
        try:
            data = [o.to_dict() for o in orders]
            with open(self.JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[OrderRepository] JSON write error: {e}")

    def load_from_json(self) -> list[BaseOrder]:
        """Read orders from the JSON file. Returns [] if file missing."""
        if not os.path.exists(self.JSON_PATH):
            return []
        try:
            with open(self.JSON_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [OrderFactory.from_dict(d) for d in raw]
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"[OrderRepository] JSON read error: {e}")
            return []

    # ── CSV ───────────────────────────────────
    def export_to_csv(self, orders: list[BaseOrder]) -> None:
        """Export orders to a CSV file (e.g. for Excel / reporting)."""
        try:
            with open(self.CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.CSV_FIELDS, extrasaction="ignore"
                )
                writer.writeheader()
                for o in orders:
                    writer.writerow(o.to_dict())
        except OSError as e:
            print(f"[OrderRepository] CSV write error: {e}")

    def load_from_csv(self) -> list[dict]:
        """Read raw rows from the CSV file. Returns list of dicts."""
        if not os.path.exists(self.CSV_PATH):
            return []
        try:
            with open(self.CSV_PATH, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except OSError as e:
            print(f"[OrderRepository] CSV read error: {e}")
            return []