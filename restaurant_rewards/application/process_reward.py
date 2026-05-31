"""Caso de uso del lado de recompensas (consumidor).

Recibe un evento ``DinnerRegistered``, calcula la recompensa con la politica
de dominio, actualiza la cuenta del cliente y publica ``RewardProcessed`` para
habilitar la notificacion opcional. Depende solo de puertos abstractos.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from ..domain.events import DinnerRegistered, RewardProcessed
from ..domain.model import Dinner
from ..domain.ports import EventPublisher, RewardAccountRepository
from ..domain.reward_policy import RewardPolicy

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProcessRewardUseCase:
    """Procesa una cena registrada y acredita la recompensa al cliente."""

    def __init__(
        self,
        repository: RewardAccountRepository,
        policy: Optional[RewardPolicy] = None,
        publisher: Optional[EventPublisher] = None,
        clock: Clock = _utc_now,
    ) -> None:
        self._repository = repository
        self._policy = policy or RewardPolicy()
        self._publisher = publisher
        self._clock = clock

    def execute(self, event: DinnerRegistered) -> RewardProcessed:
        dinner = Dinner(
            card=event.card,
            restaurant=event.restaurant,
            amount=event.amount,
            occurred_at=event.occurred_at,
        )
        reward = self._policy.calculate(dinner)

        account = self._repository.get(event.card)
        account.apply(reward)
        self._repository.save(account)

        result = RewardProcessed(
            card=event.card,
            restaurant=event.restaurant,
            points_awarded=reward.points,
            cashback_awarded=reward.cashback,
            total_points=account.points,
            total_cashback=account.cashback,
            processed_at=self._clock(),
        )
        if self._publisher is not None:
            self._publisher.publish(result)
        return result
