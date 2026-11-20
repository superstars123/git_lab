from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from singleton import Dice

if TYPE_CHECKING:
    from hero import Hero


class DamageHandler(ABC):
    def __init__(self, next_handler: DamageHandler | None = None) -> None:
        self.next_handler = next_handler

    def handle(self, damage: int, hero: Hero) -> int:
        if damage <= 0:
            return 0
        remaining = self.process(damage, hero)
        if remaining > 0 and self.next_handler is not None:
            return self.next_handler.handle(remaining, hero)
        return max(0, remaining)

    @abstractmethod
    def process(self, damage: int, hero: Hero) -> int: ...


class EvasionHandler(DamageHandler):
    def __init__(self, next_handler: DamageHandler | None = None,
                 chance: float = 0.10) -> None:
        super().__init__(next_handler)
        if not 0 <= chance <= 1:
            raise ValueError("Шанс уклонения должен быть от 0 до 1")
        self.chance = chance

    def process(self, damage: int, hero: Hero) -> int:
        return 0 if Dice().chance(self.chance) else damage


class ArmorHandler(DamageHandler):
    def process(self, damage: int, hero: Hero) -> int:
        return max(1, round(damage * (1 - hero.armor.defense)))


class BarrierHandler(DamageHandler):
    def process(self, damage: int, hero: Hero) -> int:
        absorption = min(damage, hero.barrier_points)
        hero.barrier_points -= absorption
        return damage - absorption


def create_defense_chain(evasion_chance: float = 0.10) -> DamageHandler:
    return EvasionHandler(ArmorHandler(BarrierHandler()), chance=evasion_chance)
