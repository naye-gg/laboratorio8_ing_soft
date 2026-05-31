"""Microservicio del restaurante (productor).

Registra una cena recibida por linea de comandos y publica el evento
``DinnerRegistered`` en RabbitMQ. Es el "composition root" del productor:
el unico lugar donde se conoce la tecnologia concreta.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from ..application.register_dinner import (
    RegisterDinnerCommand,
    RegisterDinnerUseCase,
)
from ..domain.value_objects import DomainError
from ..infrastructure.config import RabbitMQConfig
from ..infrastructure.messaging.connection import create_connection
from ..infrastructure.messaging.rabbitmq_publisher import RabbitMQEventPublisher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Registra una cena y publica el evento.")
    parser.add_argument("--card", required=True, help="Numero de tarjeta del cliente")
    parser.add_argument("--restaurant", required=True, help="Codigo del restaurante afiliado")
    parser.add_argument("--amount", required=True, help="Monto consumido")
    return parser


def parse_command(argv: list[str]) -> RegisterDinnerCommand:
    args = build_parser().parse_args(argv)
    return RegisterDinnerCommand(
        card_number=args.card,
        restaurant_code=args.restaurant,
        amount=args.amount,
        occurred_at=datetime.now(timezone.utc),
    )


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - requiere broker real
    command = parse_command(argv if argv is not None else sys.argv[1:])
    config = RabbitMQConfig.from_env()
    connection = create_connection(config)
    try:
        channel = connection.channel()
        publisher = RabbitMQEventPublisher(
            channel, config.queue, config.notification_queue
        )
        use_case = RegisterDinnerUseCase(publisher)
        try:
            event = use_case.execute(command)
        except DomainError as exc:
            print(f" [!] Cena invalida: {exc}")
            return 1
        print(f" [x] Cena registrada y publicada: {event.restaurant} {event.card}")
        return 0
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
