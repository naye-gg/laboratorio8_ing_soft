"""Pruebas de entidades y agregados del dominio."""

from datetime import datetime, timezone

import pytest

from restaurant_rewards.domain.model import Dinner, Reward, RewardAccount
from restaurant_rewards.domain.value_objects import (
    CardNumber,
    DomainError,
    Money,
    RestaurantCode,
)


def make_dinner(amount="100.00"):
    return Dinner(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        amount=Money.of(amount),
        occurred_at=datetime(2026, 5, 30, 20, 0, tzinfo=timezone.utc),
    )


class TestDinner:
    def test_cena_valida(self):
        assert make_dinner().amount.amount.compare(Money.of("100").amount) == 0

    def test_rechaza_monto_cero(self):
        with pytest.raises(DomainError):
            make_dinner("0")


class TestReward:
    def test_rechaza_puntos_negativos(self):
        with pytest.raises(DomainError):
            Reward(points=-1, cashback=Money(0))


class TestRewardAccount:
    def test_apply_acumula_puntos_y_cashback(self):
        account = RewardAccount(card=CardNumber("4111111111111111"))
        account.apply(Reward(points=10, cashback=Money.of("5")))
        account.apply(Reward(points=5, cashback=Money.of("2.50")))
        assert account.points == 15
        assert account.cashback.amount == Money.of("7.50").amount

    def test_snapshot_es_copia_independiente(self):
        account = RewardAccount(card=CardNumber("4111111111111111"), points=3)
        copy = account.snapshot()
        account.apply(Reward(points=2, cashback=Money(0)))
        assert copy.points == 3
        assert account.points == 5
