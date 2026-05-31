"""Pruebas de adaptadores de infraestructura (repositorio, config, RabbitMQ)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from restaurant_rewards.domain.events import DinnerRegistered, RewardProcessed
from restaurant_rewards.domain.value_objects import CardNumber, Money, RestaurantCode
from restaurant_rewards.infrastructure.config import RabbitMQConfig
from restaurant_rewards.infrastructure.messaging.rabbitmq_consumer import (
    RabbitMQEventConsumer,
)
from restaurant_rewards.infrastructure.messaging.rabbitmq_publisher import (
    RabbitMQEventPublisher,
)
from restaurant_rewards.infrastructure.persistence.in_memory_account_repository import (
    InMemoryRewardAccountRepository,
)


class TestInMemoryRepository:
    def test_get_crea_cuenta_si_no_existe(self):
        repo = InMemoryRewardAccountRepository()
        card = CardNumber("4111111111111111")

        account = repo.get(card)

        assert account.card.value == card.value
        assert len(repo) == 1

    def test_save_persiste_estado(self):
        repo = InMemoryRewardAccountRepository()
        card = CardNumber("4111111111111111")
        account = repo.get(card)
        account.points = 99
        repo.save(account)

        assert repo.get(card).points == 99


class TestRabbitMQConfig:
    def test_valores_por_defecto(self):
        config = RabbitMQConfig.from_env(env={})
        assert config.host == "localhost"
        assert config.port == 5672
        assert config.virtual_host == "/"

    def test_lee_variables_de_entorno(self):
        config = RabbitMQConfig.from_env(
            env={"RABBITMQ_HOST": "localhost", "RABBITMQ_PORT": "5673"}
        )
        assert config.host == "localhost"
        assert config.port == 5673

    def test_password_no_se_expone_en_repr(self):
        config = RabbitMQConfig(password="secreto")
        assert "secreto" not in repr(config)


def _dinner_event():
    return DinnerRegistered(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        amount=Money.of("50"),
        occurred_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
    )


def _reward_event():
    return RewardProcessed(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        points_awarded=50,
        cashback_awarded=Money.of("2.50"),
        total_points=50,
        total_cashback=Money.of("2.50"),
        processed_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
    )


class TestRabbitMQPublisher:
    def test_declara_colas_al_construirse(self):
        channel = MagicMock()
        RabbitMQEventPublisher(channel, "cenas", "notificaciones")
        declaradas = {c.kwargs["queue"] for c in channel.queue_declare.call_args_list}
        assert declaradas == {"cenas", "notificaciones"}

    def test_publica_dinner_en_cola_principal(self):
        channel = MagicMock()
        publisher = RabbitMQEventPublisher(channel, "cenas", "notificaciones")

        publisher.publish(_dinner_event())

        args = channel.basic_publish.call_args.kwargs
        assert args["routing_key"] == "cenas"
        assert b"dinner.registered" in args["body"]

    def test_publica_reward_en_cola_de_notificaciones(self):
        channel = MagicMock()
        publisher = RabbitMQEventPublisher(channel, "cenas", "notificaciones")

        publisher.publish(_reward_event())

        args = channel.basic_publish.call_args.kwargs
        assert args["routing_key"] == "notificaciones"
        assert b"reward.processed" in args["body"]

    def test_una_sola_cola_no_declara_duplicado(self):
        # Sin cola de notificacion separada, solo se declara una cola.
        channel = MagicMock()
        RabbitMQEventPublisher(channel, "cenas")
        assert channel.queue_declare.call_count == 1


class TestRabbitMQConsumer:
    def test_handle_message_valido_invoca_handler(self):
        channel = MagicMock()
        consumer = RabbitMQEventConsumer(channel, "cenas")
        recibidos = []

        from restaurant_rewards.infrastructure.serialization import (
            dinner_registered_to_json,
        )

        body = dinner_registered_to_json(_dinner_event()).encode("utf-8")
        ok = consumer.handle_message(recibidos.append, body)

        assert ok is True
        assert len(recibidos) == 1
        assert recibidos[0].restaurant.value == "REST-001"

    def test_handle_message_invalido_se_descarta(self):
        channel = MagicMock()
        consumer = RabbitMQEventConsumer(channel, "cenas")
        recibidos = []

        ok = consumer.handle_message(recibidos.append, b"basura")

        assert ok is False
        assert recibidos == []
