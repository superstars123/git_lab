from __future__ import annotations
from combat import Hit
from enemies import Enemy


class EnemyDecorator(Enemy):

    def __init__(self, enemy: Enemy) -> None:
        self._enemy = enemy
        self.code = enemy.code

    @property
    def name(self) -> str:
        return self._enemy.name

    @property
    def health(self) -> int:
        return self._enemy.health

    @property
    def max_health(self) -> int:
        return self._enemy.max_health

    @property
    def experience_reward(self) -> int:
        return self._enemy.experience_reward

    @property
    def gold_reward(self) -> int:
        return self._enemy.gold_reward

    def roll_gold_reward(self) -> int:
        return self._enemy.roll_gold_reward()

    def roll_damage(self) -> Hit:
        return self._enemy.roll_damage()

    def receive_hit(self, damage: int) -> int:
        return self._enemy.receive_hit(damage)


class FrenziedEnemy(EnemyDecorator):

    @property
    def name(self) -> str:
        return f"Яростный {super().name}"

    def roll_damage(self) -> Hit:
        hit = super().roll_damage()
        return Hit(max(1, round(hit.damage * 1.25)), hit.critical)


class ArmoredEnemy(EnemyDecorator):

    @property
    def name(self) -> str:
        return f"Бронированный {super().name}"

    def receive_hit(self, damage: int) -> int:
        return super().receive_hit(max(1, round(damage * 0.8)))


class LegendaryEnemy(EnemyDecorator):

    @property
    def name(self) -> str:
        return f"Легендарный {super().name}"

    @property
    def experience_reward(self) -> int:
        return round(super().experience_reward * 1.5)
