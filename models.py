import json
import csv
import os
from datetime import datetime


class BaseOrder:
    VALID_STATUSES = ('new', 'in_progress', 'ready', 'delivered', 'cancelled')

    def __init__(self, chat_id: int, username: str):
        self.order_id: int | None = None
        self.chat_id: int = chat_id
        self.username: str = username or "unknown"
        self.status: str = "new"
        self.created_at: datetime = datetime.now()

    def advance_status(self) -> str:
        flow = {
            'new':         'in_progress',
            'in_progress': 'ready',
            'ready':       'delivered',
        }
        if self.status in flow:
            self.status = flow[self.status]
        return self.status

    def cancel(self):
        self.status = 'cancelled'

    def is_active(self) -> bool:
        return self.status not in ('delivered', 'cancelled')

    def to_dict(self) -> dict:
        return {
            "order_id":   self.order_id,
            "chat_id":    self.chat_id,
            "username":   self.username,
            "status":     self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BaseOrder":
        obj = cls(data["chat_id"], data["username"])
        obj.order_id   = data.get("order_id")
        obj.status     = data.get("status", "new")
        obj.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%d %H:%M:%S"
        )
        return obj


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.order_id}, user={self.username}, status={self.status})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseOrder):
            return NotImplemented
        return self.order_id == other.order_id


class CakeOrder(BaseOrder):
    def __init__(
        self,
        chat_id:  int,
        username: str,
        flavor:   str = "",
        size:     str = "",
        photo_id: str = "",
        extras:   str = "",
    ):
        super().__init__(chat_id, username)   
        self.flavor:   str = flavor
        self.size:     str = size
        self.photo_id: str = photo_id
        self.extras:   str = extras

    def to_dict(self) -> dict:
        base = super().to_dict()         
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

class CustomOrder(CakeOrder):
    def __init__(self, chat_id: int, username: str, **kwargs):
        super().__init__(chat_id, username, **kwargs)
        self.needs_review: bool = True

    def summary(self) -> str:
        base = super().summary()       
        return base + "\n⚠️  Custom order — manual review required."

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["type"] = "custom"
        base["needs_review"] = self.needs_review
        return base

class OrderFactory:
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
        t = data.get("type", "cake")
        if t == "custom":
            return CustomOrder.from_dict(data)
        return CakeOrder.from_dict(data)

class OrderRepository:
    JSON_PATH = "orders_backup.json"
    CSV_PATH  = "orders_export.csv"
    CSV_FIELDS = [
        "order_id", "chat_id", "username", "flavor",
        "size", "extras", "status", "created_at", "type",
    ]

    def save_to_json(self, orders: list[BaseOrder]) -> None:
        try:
            data = [o.to_dict() for o in orders]
            with open(self.JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[OrderRepository] JSON write error: {e}")

    def load_from_json(self) -> list[BaseOrder]:
        if not os.path.exists(self.JSON_PATH):
            return []
        try:
            with open(self.JSON_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [OrderFactory.from_dict(d) for d in raw]
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"[OrderRepository] JSON read error: {e}")
            return []

    def export_to_csv(self, orders: list[BaseOrder]) -> None:
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
        if not os.path.exists(self.CSV_PATH):
            return []
        try:
            with open(self.CSV_PATH, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except OSError as e:
            print(f"[OrderRepository] CSV read error: {e}")
            return []