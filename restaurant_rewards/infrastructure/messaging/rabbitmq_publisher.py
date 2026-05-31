"""Adaptador de salida: publica eventos en colas de RabbitMQ.

Implementa el puerto ``EventPublisher``. El canal de RabbitMQ se inyecta, lo
que permite probar el adaptador con un doble de prueba sin levantar el broker.
"""

from __future__ import annotations

from ...domain.events import DinnerRegistered, RewardProcessed
from ..serialization import (
    dinner_registered_to_json,
    reward_processed_to_json,
)


class RabbitMQEventPublisher:
    """Publica eventos de dominio serializados como JSON en una cola."""

    def __init__(self, channel, queue: str, notification_queue: str | None = None) -> None:
        self._channel = channel
        self._queue = queue
        self._notification_queue = notification_queue or queue
        self._declare(self._queue)
        if self._notification_queue != self._queue:
            self._declare(self._notification_queue)

    def _declare(self, queue: str) -> None:
        self._channel.queue_declare(queue=queue, durable=True)

    def publish(self, event: object) -> None:
        if isinstance(event, DinnerRegistered):
            self._send(self._queue, dinner_registered_to_json(event))
        elif isinstance(event, RewardProcessed):
            self._send(self._notification_queue, reward_processed_to_json(event))
        else:  # pragma: no cover - guardado defensivo
            raise TypeError(f"Tipo de evento no soportado: {type(event)!r}")

    def _send(self, queue: str, body: str) -> None:
        self._channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body.encode("utf-8"),
        )
