"""Eventos de dominio que viajan por el broker de mensajeria.

Los eventos son el contrato de integracion entre los microservicios. Al ser
estructuras inmutables y autocontenidas, permiten un acoplamiento minimo:
el productor y el consumidor solo comparten la forma del evento, no el codigo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .value_objects import CardNumber, Money, RestaurantCode


@dataclass(frozen=True)
class DinnerRegistered:
    """Evento publicado cuando un restaurante registra una cena.

    Contiene exactamente la informacion exigida por el enunciado:
    monto consumido, numero de tarjeta, codigo de restaurante y fecha/hora.
    """

    card: CardNumber
    restaurant: RestaurantCode
    amount: Money
    occurred_at: datetime

    name: str = "dinner.registered"


@dataclass(frozen=True)
class RewardProcessed:
    """Evento publicado cuando la recompensa de una cena ya fue calculada.

    Habilita el paso opcional de notificacion (correo/SMS/app) sin acoplar
    el calculo de recompensas con el canal de notificacion.
    """

    card: CardNumber
    restaurant: RestaurantCode
    points_awarded: int
    cashback_awarded: Money
    total_points: int
    total_cashback: Money
    processed_at: datetime

    name: str = "reward.processed"
