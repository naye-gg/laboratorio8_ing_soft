"""Configuracion de la conexion al broker leida desde variables de entorno.

Mantener la configuracion fuera del codigo evita credenciales embebidas y
facilita desplegar en distintos entornos. Por seguridad, la contrasena no se
imprime en ``__repr__``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RabbitMQConfig:
    """Parametros de conexion a RabbitMQ."""

    host: str = "localhost"
    port: int = 5672
    virtual_host: str = "/"
    username: str = "students"
    password: str = field(default="", repr=False)
    queue: str = "recompensas.cenas"
    notification_queue: str = "recompensas.notificaciones"

    @classmethod
    def from_env(cls, env: dict | None = None) -> "RabbitMQConfig":
        source = env if env is not None else os.environ
        return cls(
            host=source.get("RABBITMQ_HOST", "localhost"),
            port=int(source.get("RABBITMQ_PORT", "5672")),
            virtual_host=source.get("RABBITMQ_VHOST", "/"),
            username=source.get("RABBITMQ_USER", "students"),
            password=source.get("RABBITMQ_PASSWORD", ""),
            queue=source.get("RABBITMQ_QUEUE", "recompensas.cenas"),
            notification_queue=source.get(
                "RABBITMQ_NOTIFICATION_QUEUE", "recompensas.notificaciones"
            ),
        )
