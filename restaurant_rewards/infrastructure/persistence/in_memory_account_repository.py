"""Repositorio de cuentas en memoria (adaptador del puerto de persistencia).

Implementacion simple y testeable. Al respetar el puerto
``RewardAccountRepository`` puede sustituirse por una base de datos real sin
afectar a los casos de uso.
"""

from __future__ import annotations

from typing import Dict

from ...domain.model import RewardAccount
from ...domain.value_objects import CardNumber


class InMemoryRewardAccountRepository:
    """Almacena cuentas de recompensas indexadas por numero de tarjeta."""

    def __init__(self) -> None:
        self._accounts: Dict[str, RewardAccount] = {}

    def get(self, card: CardNumber) -> RewardAccount:
        account = self._accounts.get(card.value)
        if account is None:
            account = RewardAccount(card=card)
            self._accounts[card.value] = account
        return account

    def save(self, account: RewardAccount) -> None:
        self._accounts[account.card.value] = account

    def __len__(self) -> int:
        return len(self._accounts)
