"""Pruebas del caso de uso de registro de cena (lado productor)."""

from datetime import datetime, timezone

import pytest

from restaurant_rewards.application.register_dinner import (
    RegisterDinnerCommand,
    RegisterDinnerUseCase,
)
from restaurant_rewards.domain.events import DinnerRegistered
from restaurant_rewards.domain.value_objects import DomainError
from tests.fakes import FakePublisher


def command(amount="80.00"):
    return RegisterDinnerCommand(
        card_number="4111111111111111",
        restaurant_code="rest-001",
        amount=amount,
        occurred_at=datetime(2026, 5, 30, 21, 30, tzinfo=timezone.utc),
    )


def test_publica_evento_dinner_registered():
    publisher = FakePublisher()
    use_case = RegisterDinnerUseCase(publisher)

    event = use_case.execute(command())

    assert isinstance(event, DinnerRegistered)
    assert len(publisher.published) == 1
    publicado = publisher.published[0]
    assert publicado.restaurant.value == "REST-001"
    assert publicado.amount.amount == event.amount.amount
    assert event.name == "dinner.registered"


def test_rechaza_comando_invalido_y_no_publica():
    publisher = FakePublisher()
    use_case = RegisterDinnerUseCase(publisher)

    with pytest.raises(DomainError):
        use_case.execute(command("0"))

    assert publisher.published == []
