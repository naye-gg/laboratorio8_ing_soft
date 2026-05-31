"""Objetos de valor del dominio.

Los objetos de valor son inmutables, se comparan por su contenido y
encapsulan invariantes de negocio. Su alta cohesion evita que las reglas
de validacion se dispersen por el resto del sistema.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

_CENTS = Decimal("0.01")


class DomainError(ValueError):
    """Error de validacion de una invariante del dominio."""


@dataclass(frozen=True)
class Money:
    """Importe monetario no negativo con precision de dos decimales."""

    amount: Decimal

    def __post_init__(self) -> None:
        try:
            normalized = Decimal(self.amount).quantize(_CENTS, rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError) as exc:
            raise DomainError(f"Importe monetario invalido: {self.amount!r}") from exc
        if normalized < Decimal("0"):
            raise DomainError("El importe no puede ser negativo")
        # Reasignacion permitida pese a frozen: usamos object.__setattr__.
        object.__setattr__(self, "amount", normalized)

    @classmethod
    def of(cls, value: str | int | float | Decimal) -> "Money":
        """Construye un ``Money`` a partir de tipos primitivos comunes.

        Delega la conversion en ``__post_init__`` para centralizar el manejo
        de valores invalidos en un unico punto.
        """
        if isinstance(value, float):
            value = str(value)
        return cls(value)  # type: ignore[arg-type]

    def multiplied_by(self, factor: Decimal) -> "Money":
        return Money(self.amount * Decimal(factor))

    def units(self) -> int:
        """Parte entera del importe (unidades monetarias completas)."""
        return int(self.amount.to_integral_value(rounding="ROUND_DOWN"))

    def __str__(self) -> str:
        return f"{self.amount:.2f}"


@dataclass(frozen=True)
class CardNumber:
    """Numero de tarjeta del cliente.

    Por seguridad, el valor nunca se expone completo: ``masked`` solo revela
    los ultimos cuatro digitos, evitando filtrar datos sensibles en logs.
    """

    value: str

    def __post_init__(self) -> None:
        digits = str(self.value).replace(" ", "").replace("-", "")
        if not digits.isdigit():
            raise DomainError("El numero de tarjeta debe contener solo digitos")
        if not 13 <= len(digits) <= 19:
            raise DomainError("El numero de tarjeta debe tener entre 13 y 19 digitos")
        object.__setattr__(self, "value", digits)

    @property
    def masked(self) -> str:
        return f"****{self.value[-4:]}"

    def __str__(self) -> str:
        return self.masked


@dataclass(frozen=True)
class RestaurantCode:
    """Codigo del restaurante afiliado."""

    value: str

    def __post_init__(self) -> None:
        code = str(self.value).strip().upper()
        if not code:
            raise DomainError("El codigo de restaurante no puede estar vacio")
        if len(code) > 32:
            raise DomainError("El codigo de restaurante es demasiado largo")
        object.__setattr__(self, "value", code)

    def __str__(self) -> str:
        return self.value
