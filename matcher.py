from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class VehiclePreferences:
    vehicle_types: tuple[str, ...] = ()
    transmission: str = ""
    fuel: str = ""
    priorities: tuple[str, ...] = ()
    usage: str = ""


@dataclass(frozen=True)
class VehicleMatch:
    vehicle_id: int
    score: int
    reasons: tuple[str, ...]


PRIORITY_FEATURES = {
    "confort": ("climatizador", "cuero", "techo", "asientos eléctricos", "acceso sin llave"),
    "tecnologia": ("carplay", "android auto", "multimedia", "wi-fi", "pantalla", "cámara 360"),
    "seguridad": ("airbags", "adas", "estabilidad", "punto ciego", "cámara", "sensores"),
    "ruta": ("control crucero", "control de velocidad crucero", "climatizador", "adas"),
    "ciudad": ("cámara", "sensores", "automática", "compacto"),
}


def _norm(value: object) -> str:
    return str(value or "").strip().lower()


def _feature_text(vehicle: dict) -> str:
    return " ".join(_norm(item) for item in vehicle.get("features", []))


def score_vehicle(vehicle: dict, preferences: VehiclePreferences) -> VehicleMatch:
    points = 0.0
    reasons: list[str] = []

    wanted_types = {_norm(item) for item in preferences.vehicle_types if _norm(item)}
    vehicle_type = _norm(vehicle.get("type"))
    if wanted_types:
        if vehicle_type in wanted_types:
            points += 40
            reasons.append(f"tipo {vehicle.get('type')} compatible")
    else:
        points += 15

    if preferences.transmission:
        if _norm(vehicle.get("transmission")) == _norm(preferences.transmission):
            points += 20
            reasons.append(f"transmisión {vehicle.get('transmission')}")
    else:
        points += 8

    if preferences.fuel:
        if _norm(vehicle.get("fuel")) == _norm(preferences.fuel):
            points += 10
            reasons.append(f"combustible {vehicle.get('fuel')}")
    else:
        points += 4

    feature_text = _feature_text(vehicle)
    matched_priorities = 0
    for priority in preferences.priorities:
        keywords = PRIORITY_FEATURES.get(_norm(priority), ())
        if keywords and any(keyword in feature_text for keyword in keywords):
            matched_priorities += 1
            reasons.append(f"prioriza {_norm(priority)}")
    if preferences.priorities:
        points += min(20, (matched_priorities / len(preferences.priorities)) * 20)
    else:
        points += 8

    usage = _norm(preferences.usage)
    if usage:
        usage_bonus = 0
        if usage == "familia" and vehicle_type in {"suv", "pickup", "auto"}:
            usage_bonus = 10
        elif usage == "ciudad" and vehicle_type in {"auto", "hatchback"}:
            usage_bonus = 10
        elif usage in {"trabajo", "carga"} and vehicle_type == "pickup":
            usage_bonus = 10
        elif usage == "ruta" and any(k in feature_text for k in PRIORITY_FEATURES["ruta"]):
            usage_bonus = 10
        if usage_bonus:
            points += usage_bonus
            reasons.append(f"encaja con uso {usage}")
    else:
        points += 5

    score = max(0, min(100, round(points)))
    if not reasons:
        reasons.append("coincidencia general con el stock disponible")
    return VehicleMatch(vehicle_id=int(vehicle["id"]), score=score, reasons=tuple(reasons))


def rank_vehicles(vehicles: Iterable[dict], preferences: VehiclePreferences) -> list[VehicleMatch]:
    matches = [score_vehicle(vehicle, preferences) for vehicle in vehicles]
    return sorted(matches, key=lambda item: (-item.score, item.vehicle_id))


def profile_vehicle(vehicle: dict) -> dict:
    vehicle_type = _norm(vehicle.get("type"))
    features = _feature_text(vehicle)

    traits: list[str] = []
    if vehicle_type == "pickup":
        traits.extend(["robusta", "trabajo", "aventura"])
    elif vehicle_type == "suv":
        traits.extend(["versátil", "familiar", "presencia"])
    else:
        traits.extend(["urbano", "equilibrado"])

    if "techo panorámico" in features or "cuero" in features:
        traits.append("confort")
    if "adas" in features or "punto ciego" in features or "airbags" in features:
        traits.append("seguridad")
    if "carplay" in features or "android auto" in features or "multimedia" in features:
        traits.append("tecnológico")
    if int(vehicle.get("km", 0) or 0) < 30000:
        traits.append("bajo kilometraje")

    unique_traits = list(dict.fromkeys(traits))
    return {
        "segment": vehicle.get("type", ""),
        "traits": unique_traits,
        "vibe": " · ".join(unique_traits[:3]),
    }
