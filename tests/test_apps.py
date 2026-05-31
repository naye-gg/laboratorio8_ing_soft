"""Pruebas de los puntos de entrada (parseo de comandos y manejadores)."""

from restaurant_rewards.application.process_reward import ProcessRewardUseCase
from restaurant_rewards.apps.consumer_app import build_handler
from restaurant_rewards.apps.producer_app import parse_command
from restaurant_rewards.domain.events import DinnerRegistered
from restaurant_rewards.domain.value_objects import CardNumber, Money, RestaurantCode
from restaurant_rewards.infrastructure.persistence.in_memory_account_repository import (
    InMemoryRewardAccountRepository,
)
from datetime import datetime, timezone


def test_parse_command_construye_comando():
    command = parse_command(
        ["--card", "4111111111111111", "--restaurant", "rest-001", "--amount", "75.50"]
    )
    assert command.card_number == "4111111111111111"
    assert command.restaurant_code == "rest-001"
    assert command.amount == "75.50"
    assert command.occurred_at.tzinfo is not None


def test_build_handler_procesa_evento(capsys):
    use_case = ProcessRewardUseCase(repository=InMemoryRewardAccountRepository())
    handler = build_handler(use_case)

    handler(
        DinnerRegistered(
            card=CardNumber("4111111111111111"),
            restaurant=RestaurantCode("REST-001"),
            amount=Money.of("50"),
            occurred_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
        )
    )

    salida = capsys.readouterr().out
    assert "Recompensa procesada" in salida
    assert "****1111" in salida
