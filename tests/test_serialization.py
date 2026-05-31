"""Pruebas de serializacion de eventos."""

from datetime import datetime, timezone

import pytest

from restaurant_rewards.domain.events import DinnerRegistered, RewardProcessed
from restaurant_rewards.domain.value_objects import CardNumber, Money, RestaurantCode
from restaurant_rewards.infrastructure.serialization import (
    SerializationError,
    dinner_registered_from_json,
    dinner_registered_to_json,
    reward_processed_to_json,
)


def test_dinner_registered_round_trip():
    original = DinnerRegistered(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        amount=Money.of("123.45"),
        occurred_at=datetime(2026, 5, 30, 20, 0, tzinfo=timezone.utc),
    )

    restored = dinner_registered_from_json(dinner_registered_to_json(original))

    assert restored.card.value == original.card.value
    assert restored.restaurant.value == original.restaurant.value
    assert restored.amount.amount == original.amount.amount
    assert restored.occurred_at == original.occurred_at


def test_reward_processed_enmascara_tarjeta():
    event = RewardProcessed(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        points_awarded=10,
        cashback_awarded=Money.of("2.50"),
        total_points=10,
        total_cashback=Money.of("2.50"),
        processed_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
    )

    payload = reward_processed_to_json(event)

    assert "****1111" in payload
    assert "4111111111111111" not in payload


@pytest.mark.parametrize(
    "raw",
    [
        "no es json",
        "[1, 2, 3]",
        '{"card": "4111111111111111"}',
        '{"card": "x", "restaurant": "R", "amount": "10", "occurred_at": "2026-05-30T00:00:00"}',
    ],
)
def test_mensajes_invalidos_lanzan_serialization_error(raw):
    with pytest.raises(SerializationError):
        dinner_registered_from_json(raw)
