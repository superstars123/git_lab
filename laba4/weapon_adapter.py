from __future__ import annotations

"""Lab 4 / Adapter: turn an existing Weapon into an Enemy interface."""
from combat import Hit
from enemies import Enemy
from prototype import Weapon


class HauntedWeapon(Enemy):
    """The existing weapon provides strikes; Enemy provides health and rewards."""

    def __init__(self, weapon: Weapon) -> None:
        super().__init__("haunted-weapon", f"Ожившее оружие: {weapon.name}",
                         health=85, min_damage=1, max_damage=1,
                         experience_reward=65, gold_reward=55)
        self.weapon = weapon

    def roll_damage(self) -> Hit:
        return self.weapon.roll_damage()
