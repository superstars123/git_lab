from __future__ import annotations
from abc import ABC, abstractmethod
from combat import Combatant, Hit


class BattleTactic(ABC):
    @property
    @abstractmethod
    def title(self) -> str: ...

    @abstractmethod
    def hero_hit(self, hero: Combatant) -> Hit: ...

    @abstractmethod
    def enemy_hit(self, enemy: Combatant) -> Hit: ...


class BalancedTactic(BattleTactic):
    title = "Сбалансированная"

    def hero_hit(self, hero: Combatant) -> Hit:
        return hero.roll_damage()

    def enemy_hit(self, enemy: Combatant) -> Hit:
        return enemy.roll_damage()


class AggressiveTactic(BattleTactic):
    title = "Агрессивная (+25% наносимого и +15% получаемого урона)"

    def hero_hit(self, hero: Combatant) -> Hit:
        hit = hero.roll_damage()
        return Hit(max(1, round(hit.damage * 1.25)), hit.critical)

    def enemy_hit(self, enemy: Combatant) -> Hit:
        hit = enemy.roll_damage()
        return Hit(max(1, round(hit.damage * 1.15)), hit.critical)


class CautiousTactic(BattleTactic):
    title = "Осторожная (-15% наносимого и -25% получаемого урона)"

    def hero_hit(self, hero: Combatant) -> Hit:
        hit = hero.roll_damage()
        return Hit(max(1, round(hit.damage * 0.85)), hit.critical)

    def enemy_hit(self, enemy: Combatant) -> Hit:
        hit = enemy.roll_damage()
        return Hit(max(1, round(hit.damage * 0.75)), hit.critical)


TACTICS: dict[str, type[BattleTactic]] = {
    "balanced": BalancedTactic,
    "aggressive": AggressiveTactic,
    "cautious": CautiousTactic,
}
