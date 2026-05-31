"""Politica de calculo de recompensas (servicio de dominio).

Encapsula la regla de negocio "como se transforma el consumo en beneficios".
Aislarla en su propia clase permite cambiar la estrategia de fidelizacion sin
tocar los casos de uso ni la infraestructura (alta cohesion, bajo acoplamiento).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .model import Dinner, Reward
from .value_objects import DomainError, Money


@dataclass(frozen=True)
class RewardPolicy:
    """Calcula puntos y cashback a partir de una cena.

    - ``points_per_unit``: puntos otorgados por cada unidad monetaria entera.
    - ``cashback_rate``: fraccion del monto devuelta como reembolso.
    - ``premium_threshold`` / ``premium_multiplier``: bonificacion para
      consumos altos (escalonado de fidelizacion).
    """

    points_per_unit: int = 1
    cashback_rate: Decimal = Decimal("0.05")
    premium_threshold: Money = Money(Decimal("100"))
    premium_multiplier: Decimal = Decimal("1.5")

    def __post_init__(self) -> None:
        if self.points_per_unit < 0:
            raise DomainError("points_per_unit no puede ser negativo")
        if self.cashback_rate < 0:
            raise DomainError("cashback_rate no puede ser negativo")
        if self.premium_multiplier < 1:
            raise DomainError("premium_multiplier debe ser >= 1")

    def calculate(self, dinner: Dinner) -> Reward:
        base_points = dinner.amount.units() * self.points_per_unit
        multiplier = (
            self.premium_multiplier
            if dinner.amount.amount >= self.premium_threshold.amount
            else Decimal("1")
        )
        points = int((Decimal(base_points) * multiplier).to_integral_value(rounding="ROUND_DOWN"))
        cashback = dinner.amount.multiplied_by(self.cashback_rate)
        return Reward(points=points, cashback=cashback)
