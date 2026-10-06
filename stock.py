from copy import deepcopy
from threading import RLock


class StockCatalog:
    """Owns inventory state so public views never mutate stock directly."""

    def __init__(self, vehicles):
        self._vehicles = {item["id"]: deepcopy(item) for item in vehicles}
        self._lock = RLock()

    def public_list(self, query="", vehicle_type=""):
        query = query.strip().lower()
        vehicle_type = vehicle_type.strip().lower()
        with self._lock:
            items = [deepcopy(item) for item in self._vehicles.values() if item.get("available", True)]

        return [
            item for item in items
            if (not query or query in f'{item["brand"]} {item["model"]} {item["year"]}'.lower())
            and (not vehicle_type or vehicle_type == "todos" or item["type"].lower() == vehicle_type)
        ]

    def public_get(self, vehicle_id):
        with self._lock:
            item = self._vehicles.get(vehicle_id)
            if not item or not item.get("available", True):
                return None
            return deepcopy(item)

    def admin_list(self):
        with self._lock:
            return [deepcopy(item) for item in self._vehicles.values()]

    def set_availability(self, vehicle_id, available):
        with self._lock:
            item = self._vehicles.get(vehicle_id)
            if not item:
                return None
            item["available"] = bool(available)
            return deepcopy(item)
