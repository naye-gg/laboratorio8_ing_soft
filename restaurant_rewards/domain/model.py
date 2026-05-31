"""Entidades y agregados del dominio."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime

from .value_objects import CardNumber, DomainError, Money, RestaurantCode


@dataclass(frozen=True)
class Dinner:
    """Cena registrada por un restaurante afiliado.

    Representa la transaccion de consumo que dispara todo el flujo de
    recompensas. Es inmutable: una vez registrada no cambia.
    """

    card: CardNumber
    restaurant: RestaurantCode
    amount: Money
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.amount.amount <= 0:
            raise DomainError("El monto consumido debe ser mayor que cero")


@dataclass(frozen=True)
class Reward:
    """Recompensa calculada para una cena: puntos y reembolso (cashback)."""

    points: int
    cashback: Money

    def __post_init__(self) -> None:
        if self.points < 0:
            raise DomainError("Los puntos no pueden ser negativos")


@dataclass
class RewardAccount:
    """Cuenta de recompensas de un cliente (agregado).

    Acumula puntos y cashback. Toda mutacion ocurre a traves de
    ``apply``, lo que mantiene la consistencia del agregado.
    """

    card: CardNumber
    points: int = 0
    cashback: Money = field(default_factory=lambda: Money(0))

    def apply(self, reward: Reward) -> "RewardAccount":
        """Acumula una recompensa y devuelve el nuevo estado de la cuenta."""
        self.points += reward.points
        self.cashback = Money(self.cashback.amount + reward.cashback.amount)
        return self

    def snapshot(self) -> "RewardAccount":
        """Copia inmutable del estado actual (util para lecturas seguras)."""
        return replace(self)
