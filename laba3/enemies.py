from __future__ import annotations

"""Типы противников для фабричного метода."""
from combat import Combatant, Hit
from singleton import Dice

class Enemy(Combatant):
    def __init__(self, code: str, name: str, health: int, min_damage: int,
                 max_damage: int, experience_reward: int, gold_reward: int) -> None:
        self.code = code
        self._name = name
        self._health = health
        self._max_health = health
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.experience_reward = experience_reward
        self.gold_reward = gold_reward

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._max_health

    def roll_damage(self) -> Hit:
        return Hit(Dice().roll(self.min_damage, self.max_damage))

    def reduce_damage(self, damage: int) -> int:
        return damage

    def receive_hit(self, damage: int) -> int:
        actual = max(1, self.reduce_damage(damage))
        self._health = max(0, self._health - actual)
        return actual

    def roll_gold_reward(self) -> int:
        return Dice().roll(max(1, self.gold_reward // 2), self.gold_reward)


class Goblin(Enemy):
    def __init__(self) -> None:
        super().__init__("goblin", "Гоблин", 50, 6, 14, 40, 30)


class Skeleton(Enemy):
    def __init__(self) -> None:
        super().__init__("skeleton", "Скелет", 110, 10, 24, 90, 70)

    def reduce_damage(self, damage: int) -> int:
        return round(damage * 0.70)  # сопротивление 30%


class Dragon(Enemy):
    def __init__(self) -> None:
        super().__init__("dragon", "Дракон", 260, 16, 22, 500, 400)

    def roll_damage(self) -> Hit:
        bite = super().roll_damage()
        if Dice().chance(0.25):
            return Hit(bite.damage * 2, True)  # огненное дыхание
        return bite

    def reduce_damage(self, damage: int) -> int:
        return round(damage * 0.75)  # чешуя поглощает 25%
