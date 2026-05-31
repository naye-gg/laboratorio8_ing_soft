"""Adaptador de entrada: consume eventos ``DinnerRegistered`` de RabbitMQ.

Implementa el puerto ``EventConsumer``. Traduce cada mensaje del broker a un
evento de dominio y lo entrega al manejador (caso de uso), sin que este conozca
detalles de RabbitMQ. Los mensajes invalidos se descartan de forma controlada.
"""

from __future__ import annotations

from typing import Callable

from ...domain.events import DinnerRegistered
from ..serialization import SerializationError, dinner_registered_from_json

Handler = Callable[[DinnerRegistered], None]


class RabbitMQEventConsumer:
    """Escucha una cola y enruta cada mensaje hacia un manejador de dominio."""

    def __init__(self, channel, queue: str) -> None:
        self._channel = channel
        self._queue = queue
        self._channel.queue_declare(queue=queue, durable=True)

    def handle_message(self, handler: Handler, body: bytes) -> bool:
        """Procesa un cuerpo de mensaje. Devuelve ``True`` si fue valido.

        Separar esta logica del bucle de consumo la hace facilmente testeable.
        """
        try:
            event = dinner_registered_from_json(body)
        except SerializationError:
            return False
        handler(event)
        return True

    def consume(self, handler: Handler) -> None:  # pragma: no cover - requiere broker real
        def _callback(_ch, _method, _properties, body):
            self.handle_message(handler, body)

        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=_callback,
            auto_ack=True,
        )
        self._channel.start_consuming()
