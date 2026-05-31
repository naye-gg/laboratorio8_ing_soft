"""Microservicio de recompensas (consumidor).

Escucha eventos ``DinnerRegistered`` en RabbitMQ, calcula la recompensa,
actualiza la cuenta del cliente y publica ``RewardProcessed`` para la
notificacion opcional. Es el "composition root" del consumidor.
"""

from __future__ import annotations

from ..application.process_reward import ProcessRewardUseCase
from ..domain.events import DinnerRegistered, RewardProcessed
from ..domain.ports import RewardAccountRepository
from ..domain.reward_policy import RewardPolicy
from ..infrastructure.config import RabbitMQConfig
from ..infrastructure.messaging.connection import create_connection
from ..infrastructure.messaging.rabbitmq_consumer import RabbitMQEventConsumer
from ..infrastructure.messaging.rabbitmq_publisher import RabbitMQEventPublisher
from ..infrastructure.persistence.in_memory_account_repository import (
    InMemoryRewardAccountRepository,
)


def build_handler(use_case: ProcessRewardUseCase):
    """Crea el manejador que conecta el evento entrante con el caso de uso."""

    def _handle(event: DinnerRegistered) -> None:
        result: RewardProcessed = use_case.execute(event)
        print(
            f" [x] Recompensa procesada para {result.card}: "
            f"+{result.points_awarded} pts, +{result.cashback_awarded} cashback "
            f"(total {result.total_points} pts)"
        )

    return _handle


def main() -> int:  # pragma: no cover - requiere broker real
    config = RabbitMQConfig.from_env()
    connection = create_connection(config)
    try:
        channel = connection.channel()
        repository: RewardAccountRepository = InMemoryRewardAccountRepository()
        publisher = RabbitMQEventPublisher(channel, config.queue, config.notification_queue)
        use_case = ProcessRewardUseCase(
            repository=repository,
            policy=RewardPolicy(),
            publisher=publisher,
        )
        consumer = RabbitMQEventConsumer(channel, config.queue)
        print(f' [*] Esperando cenas en la cola "{config.queue}". CTRL+C para salir.')
        try:
            consumer.consume(build_handler(use_case))
        except KeyboardInterrupt:
            print("\n [*] Deteniendo el consumidor...")
        return 0
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
