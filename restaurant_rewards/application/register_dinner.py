"""Caso de uso del lado del restaurante (productor).

Registra una cena y publica el evento ``DinnerRegistered`` en el broker.
No conoce RabbitMQ: depende del puerto ``EventPublisher``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain.events import DinnerRegistered
from ..domain.model import Dinner
from ..domain.ports import EventPublisher
from ..domain.value_objects import CardNumber, Money, RestaurantCode


@dataclass(frozen=True)
class RegisterDinnerCommand:
    """Datos de entrada para registrar una cena."""

    card_number: str
    restaurant_code: str
    amount: str
    occurred_at: datetime


class RegisterDinnerUseCase:
    """Convierte un comando en una cena valida y publica el evento."""

    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    def execute(self, command: RegisterDinnerCommand) -> DinnerRegistered:
        dinner = Dinner(
            card=CardNumber(command.card_number),
            restaurant=RestaurantCode(command.restaurant_code),
            amount=Money.of(command.amount),
            occurred_at=command.occurred_at,
        )
        event = DinnerRegistered(
            card=dinner.card,
            restaurant=dinner.restaurant,
            amount=dinner.amount,
            occurred_at=dinner.occurred_at,
        )
        self._publisher.publish(event)
        return event
