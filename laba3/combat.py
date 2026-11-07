from __future__ import annotations

"""Общие классы боевой системы."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Hit:
    damage: int
    critical: bool = False


@dataclass(frozen=True)
class BattleEvent:
    round_number: int
    attacker: str
    defender: str
    damage: int
    defender_health: int
    critical: bool = False
    death: bool = False


@dataclass(frozen=True)
class BattleReport:
    hero_name: str
    enemy_name: str
    victory: bool
    events: tuple[BattleEvent, ...]


class Combatant(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def health(self) -> int: ...

    @property
    @abstractmethod
    def max_health(self) -> int: ...

    @abstractmethod
    def roll_damage(self) -> Hit: ...

    @abstractmethod
    def receive_hit(self, damage: int) -> int: ...

    def is_alive(self) -> bool:
        return self.health > 0


class Battle:
    """Общий бой. Класс зависит от Combatant, а не от конкретных героев/врагов."""
    def __init__(self, hero: Combatant, enemy: Combatant) -> None:
        self.hero = hero
        self.enemy = enemy
        self.events: list[BattleEvent] = []

    def run(self) -> BattleReport:
        round_number = 0
        while self.hero.is_alive() and self.enemy.is_alive():
            round_number += 1
            self._strike(round_number, self.hero, self.enemy)
            if self.enemy.is_alive():
                self._strike(round_number, self.enemy, self.hero)
        return BattleReport(self.hero.name, self.enemy.name,
                            self.hero.is_alive(), tuple(self.events))

    def _strike(self, number: int, attacker: Combatant, defender: Combatant) -> None:
        hit = attacker.roll_damage()
        dealt = defender.receive_hit(hit.damage)
        event = BattleEvent(number, attacker.name, defender.name, dealt,
                            defender.health, hit.critical, not defender.is_alive())
        self.events.append(event)