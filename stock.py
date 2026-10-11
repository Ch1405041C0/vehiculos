from copy import deepcopy
from threading import RLock

VALID_STATUSES = {"BORRADOR", "PUBLICADO", "PAUSADO", "VENDIDO", "ELIMINADO"}


class StockCatalog:
    """Inventory boundary. Admin feeds stock; public channels only consume published matches."""

    def __init__(self, vehicles):
        normalized = []
        for item in vehicles:
            row = deepcopy(item)
            row.setdefault("status", "PUBLICADO" if row.get("available", True) else "PAUSADO")
            row.setdefault("finances", False)
            row.setdefault("financing_notes", "")
            row.setdefault("description", "")
            row.setdefault("images", [row.get("image")] if row.get("image") else [])
            row.setdefault("videos", [])
            normalized.append(row)
        self._vehicles = {item["id"]: item for item in normalized}
        self._lock = RLock()

    def public_list(self, query="", vehicle_type=""):
        """Temporary public selector. The matching backend can replace these filters later."""
        query = query.strip().lower()
        vehicle_type = vehicle_type.strip().lower()
        with self._lock:
            items = [deepcopy(item) for item in self._vehicles.values() if item.get("status") == "PUBLICADO"]

        return [item for item in items
                if (not query or query in f'{item["brand"]} {item["model"]} {item["year"]}'.lower())
                and (not vehicle_type or vehicle_type == "todos" or item["type"].lower() == vehicle_type)]

    def public_get(self, vehicle_id):
        with self._lock:
            item = self._vehicles.get(vehicle_id)
            if not item or item.get("status") != "PUBLICADO":
                return None
            return deepcopy(item)

    def admin_list(self):
        with self._lock:
            return [deepcopy(item) for item in self._vehicles.values() if item.get("status") != "ELIMINADO"]

    def create(self, data):
        with self._lock:
            new_id = max(self._vehicles.keys(), default=0) + 1
            item = self._normalize({**data, "id": new_id})
            self._vehicles[new_id] = item
            return deepcopy(item)

    def update(self, vehicle_id, data):
        with self._lock:
            current = self._vehicles.get(vehicle_id)
            if not current or current.get("status") == "ELIMINADO":
                return None
            current.update({k: v for k, v in data.items() if k != "id"})
            self._vehicles[vehicle_id] = self._normalize(current)
            return deepcopy(self._vehicles[vehicle_id])

    def set_status(self, vehicle_id, status):
        status = status.upper()
        if status not in VALID_STATUSES:
            raise ValueError("invalid status")
        return self.update(vehicle_id, {"status": status})

    def delete(self, vehicle_id):
        return self.set_status(vehicle_id, "ELIMINADO")

    def _normalize(self, item):
        item = deepcopy(item)
        item.setdefault("status", "BORRADOR")
        item.setdefault("brand", "")
        item.setdefault("model", "")
        item.setdefault("version", "")
        item.setdefault("year", None)
        item.setdefault("km", 0)
        item.setdefault("transmission", "")
        item.setdefault("fuel", "")
        item.setdefault("type", "")
        item.setdefault("color", "")
        item.setdefault("price", "")
        item.setdefault("finances", False)
        item.setdefault("financing_notes", "")
        item.setdefault("description", "")
        item.setdefault("images", [])
        item.setdefault("videos", [])
        item.setdefault("features", [])
        item.setdefault("tag", "")
        item["image"] = item["images"][0] if item.get("images") else ""
        return item
