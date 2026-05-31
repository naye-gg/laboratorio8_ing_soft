"""Puertos del dominio (contratos de la arquitectura hexagonal).

Los puertos son interfaces abstractas que el dominio/aplicacion necesitan.
La infraestructura provee las implementaciones concretas (adaptadores). Asi,
el nucleo no depende de RabbitMQ ni de ninguna tecnologia: depende de
abstracciones, logrando bajo acoplamiento e inversion de dependencias.
"""

from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from .events import DinnerRegistered, RewardProcessed
from .model import RewardAccount
from .value_objects import CardNumber


@runtime_checkable
class EventPublisher(Protocol):
    """Puerto de salida para publicar eventos en el broker."""

    def publish(self, event: object) -> None:
        ...


@runtime_checkable
class EventConsumer(Protocol):
    """Puerto de entrada para recibir eventos ``DinnerRegistered``."""

    def consume(self, handler: Callable[[DinnerRegistered], None]) -> None:
        ...


@runtime_checkable
class RewardAccountRepository(Protocol):
    """Puerto de salida para persistir cuentas de recompensas."""

    def get(self, card: CardNumber) -> RewardAccount:
        ...

    def save(self, account: RewardAccount) -> None:
        ...


# Tipo de conveniencia para manejadores de notificaciones.
NotificationHandler = Callable[[RewardProcessed], None]
