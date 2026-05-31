"""Serializacion de eventos de dominio hacia/desde JSON.

Aisla el formato de cable (JSON) del dominio. Los adaptadores de mensajeria
usan estas funciones para no acoplar la representacion de transporte con las
estructuras de negocio.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

from ..domain.events import DinnerRegistered, RewardProcessed
from ..domain.value_objects import CardNumber, Money, RestaurantCode


class SerializationError(ValueError):
    """El mensaje recibido no respeta el contrato del evento."""


def dinner_registered_to_json(event: DinnerRegistered) -> str:
    payload = {
        "name": event.name,
        "card": event.card.value,
        "restaurant": event.restaurant.value,
        "amount": str(event.amount.amount),
        "occurred_at": event.occurred_at.isoformat(),
    }
    return json.dumps(payload)


def dinner_registered_from_json(raw: str | bytes) -> DinnerRegistered:
    data = _load(raw)
    try:
        return DinnerRegistered(
            card=CardNumber(data["card"]),
            restaurant=RestaurantCode(data["restaurant"]),
            amount=Money(Decimal(str(data["amount"]))),
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise SerializationError(f"Evento DinnerRegistered invalido: {exc}") from exc


def reward_processed_to_json(event: RewardProcessed) -> str:
    payload = {
        "name": event.name,
        "card": event.card.masked,
        "restaurant": event.restaurant.value,
        "points_awarded": event.points_awarded,
        "cashback_awarded": str(event.cashback_awarded.amount),
        "total_points": event.total_points,
        "total_cashback": str(event.total_cashback.amount),
        "processed_at": event.processed_at.isoformat(),
    }
    return json.dumps(payload)


def _load(raw: str | bytes) -> dict:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise SerializationError(f"JSON invalido: {exc}") from exc
    if not isinstance(data, dict):
        raise SerializationError("El mensaje debe ser un objeto JSON")
    return data
