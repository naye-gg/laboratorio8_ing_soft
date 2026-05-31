"""Fabrica de conexiones a RabbitMQ.

Aisla la dependencia con ``pika`` en un unico punto. Se importa de forma
perezosa para que el resto del sistema (y las pruebas unitarias) no requieran
tener el broker ni la libreria disponibles.
"""

from __future__ import annotations

from ..config import RabbitMQConfig


def create_connection(config: RabbitMQConfig):  # pragma: no cover - requiere broker real
    """Crea una conexion bloqueante a RabbitMQ a partir de la configuracion."""
    import pika  # import perezoso: solo se necesita al hablar con el broker real

    credentials = pika.PlainCredentials(config.username, config.password)
    parameters = pika.ConnectionParameters(
        host=config.host,
        port=config.port,
        virtual_host=config.virtual_host,
        credentials=credentials,
    )
    return pika.BlockingConnection(parameters)
