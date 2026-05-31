"""Pruebas del caso de uso de procesamiento de recompensa (lado consumidor)."""

from datetime import datetime, timezone

from restaurant_rewards.application.process_reward import ProcessRewardUseCase
from restaurant_rewards.domain.events import DinnerRegistered, RewardProcessed
from restaurant_rewards.domain.value_objects import CardNumber, Money, RestaurantCode
from restaurant_rewards.infrastructure.persistence.in_memory_account_repository import (
    InMemoryRewardAccountRepository,
)
from tests.fakes import FakePublisher

FIXED_TIME = datetime(2026, 5, 30, 22, 0, tzinfo=timezone.utc)


def event(amount="50.00"):
    return DinnerRegistered(
        card=CardNumber("4111111111111111"),
        restaurant=RestaurantCode("REST-001"),
        amount=Money.of(amount),
        occurred_at=datetime(2026, 5, 30, 21, 0, tzinfo=timezone.utc),
    )


def make_use_case(publisher=None):
    return ProcessRewardUseCase(
        repository=InMemoryRewardAccountRepository(),
        publisher=publisher,
        clock=lambda: FIXED_TIME,
    )


def test_calcula_y_acredita_recompensa():
    use_case = make_use_case()

    result = use_case.execute(event("50"))

    assert isinstance(result, RewardProcessed)
    assert result.points_awarded == 50
    assert result.total_points == 50
    assert result.processed_at == FIXED_TIME


def test_acumula_en_cenas_sucesivas():
    repo = InMemoryRewardAccountRepository()
    use_case = ProcessRewardUseCase(repository=repo, clock=lambda: FIXED_TIME)

    use_case.execute(event("50"))
    result = use_case.execute(event("30"))

    assert result.total_points == 80
    assert len(repo) == 1


def test_publica_evento_de_notificacion_si_hay_publisher():
    publisher = FakePublisher()
    use_case = make_use_case(publisher)

    use_case.execute(event("50"))

    assert len(publisher.published) == 1
    assert isinstance(publisher.published[0], RewardProcessed)


def test_sin_publisher_no_falla():
    use_case = make_use_case(publisher=None)
    result = use_case.execute(event("10"))
    assert result.points_awarded == 10
