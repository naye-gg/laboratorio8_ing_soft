"""Dobles de prueba (fakes) que implementan los puertos del dominio."""

from __future__ import annotations

from typing import List


class FakePublisher:
    """Implementacion en memoria del puerto ``EventPublisher``."""

    def __init__(self) -> None:
        self.published: List[object] = []

    def publish(self, event: object) -> None:
        self.published.append(event)


class ExplodingPublisher:
    """Publisher que falla, para verificar manejo de errores."""

    def publish(self, event: object) -> None:  # pragma: no cover - trivial
        raise RuntimeError("broker caido")
