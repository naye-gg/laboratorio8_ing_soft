"""Pruebas de la politica de calculo de recompensas."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from restaurant_rewards.domain.model import Dinner
from restaurant_rewards.domain.reward_policy import RewardPolicy
from restaurant_rewards.domain.value_objects import (
    CardNumber,
    DomainError,
    Money,
    RestaurantCode,
)


def dinner(amount):
    return Dinner(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        amount=Money.of(amount),
        occurred_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
    )


class TestRewardPolicy:
    def test_calculo_estandar(self):
        reward = RewardPolicy().calculate(dinner("50"))
        assert reward.points == 50
        assert reward.cashback.amount == Decimal("2.50")

    def test_aplica_multiplicador_premium_en_umbral(self):
        # 100 * 1 punto * 1.5 = 150 puntos
        reward = RewardPolicy().calculate(dinner("100"))
        assert reward.points == 150
        assert reward.cashback.amount == Decimal("5.00")

    def test_no_aplica_premium_bajo_umbral(self):
        reward = RewardPolicy().calculate(dinner("99.99"))
        assert reward.points == 99

    def test_politica_personalizada(self):
        policy = RewardPolicy(points_per_unit=2, cashback_rate=Decimal("0.10"))
        reward = policy.calculate(dinner("20"))
        assert reward.points == 40
        assert reward.cashback.amount == Decimal("2.00")

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"points_per_unit": -1},
            {"cashback_rate": Decimal("-0.1")},
            {"premium_multiplier": Decimal("0.5")},
        ],
    )
    def test_rechaza_configuracion_invalida(self, kwargs):
        with pytest.raises(DomainError):
            RewardPolicy(**kwargs)
