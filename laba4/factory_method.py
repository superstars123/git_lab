from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable
from combat import Battle, BattleReport
from singleton import Dice
from prototype import Item, ItemCatalog, SHARP, FIERY, STURDY
from hero import Hero
from enemies import Enemy, Goblin, Skeleton, Dragon

@dataclass(frozen=True)
class Rewards:
    experience: int
    gold: int
    loot: Item | None
    levels_gained: int


@dataclass(frozen=True)
class ExpeditionReport:
    seed: int
    location_name: str
    battle: BattleReport
    rewards: Rewards


class Location(ABC):
    LOOT_CHANCE = 0.60
    ENCHANT_CHANCE = 0.30

    def __init__(self, code: str, title: str, recommended_level: int,
                 catalog: ItemCatalog) -> None:
        self.code = code
        self.title = title
        self.recommended_level = recommended_level
        self.catalog = catalog

    @abstractmethod
    def create_enemy(self) -> Enemy:
        """Фабричный метод: подкласс выбирает конкретного врага."""
        ...

    @property
    @abstractmethod
    def loot_table(self) -> tuple[str, ...]: ...

    def explore(self, hero: Hero, seed: int | None = None, tactic=None,
                enemy_decorators: tuple[Callable[[Enemy], Enemy], ...] = ()) -> ExpeditionReport:
        dice = Dice()
        if seed is None:
            seed = dice.next_seed()
        dice.reseed(seed)
        hero.restore_health()
        enemy = self.create_enemy()
        for decorator in enemy_decorators:
            enemy = decorator(enemy)
        battle_report = Battle(hero, enemy, tactic=tactic).run()
        if battle_report.victory:
            rewards = self._give_rewards(hero, enemy)
        else:
            lost = hero.gold // 2
            hero.spend_gold(lost)
            rewards = Rewards(0, -lost, None, 0)
        return ExpeditionReport(seed, self.title, battle_report, rewards)

    def _give_rewards(self, hero: Hero, enemy: Enemy) -> Rewards:
        dice = Dice()
        experience = enemy.experience_reward
        gold = enemy.roll_gold_reward()
        loot = None
        if dice.chance(self.LOOT_CHANCE):
            loot = self.catalog.create(dice.pick(self.loot_table))
            possible = (SHARP, FIERY, STURDY)
            if dice.chance(self.ENCHANT_CHANCE):
                loot.enchant(dice.pick(possible))
            hero.add_item(loot)
        levels = hero.gain_experience(experience)
        hero.add_gold(gold)
        return Rewards(experience, gold, loot, levels)


class Forest(Location):
    def __init__(self, catalog: ItemCatalog) -> None:
        super().__init__("forest", "Мистический лес", 1, catalog)

    def create_enemy(self) -> Enemy:
        return Goblin()

    @property
    def loot_table(self) -> tuple[str, ...]:
        return ("goblin-cleaver", "hunting-bow", "leather-armor")


class Crypt(Location):
    def __init__(self, catalog: ItemCatalog) -> None:
        super().__init__("crypt", "Заброшенный склеп", 3, catalog)

    def create_enemy(self) -> Enemy:
        return Skeleton()

    @property
    def loot_table(self) -> tuple[str, ...]:
        return ("knight-blade", "bone-bow", "necromancer-staff", "crypt-mail")


class DragonLair(Location):
    def __init__(self, catalog: ItemCatalog) -> None:
        super().__init__("dragon-lair", "Логово дракона", 5, catalog)

    def create_enemy(self) -> Enemy:
        return Dragon()

    @property
    def loot_table(self) -> tuple[str, ...]:
        return ("dawn-blade", "dragonscale-armor")


class HauntedArmory(Location):
    def __init__(self, catalog: ItemCatalog) -> None:
        super().__init__("haunted-armory", "Заколдованная оружейная", 2, catalog)

    def create_enemy(self) -> Enemy:
        from weapon_adapter import HauntedWeapon
        return HauntedWeapon(self.catalog.create_weapon("iron-sword"))

    @property
    def loot_table(self) -> tuple[str, ...]:
        return ("iron-sword", "chainmail", "ember-staff")


class LocationRegistry:
    def __init__(self, locations: tuple[Location, ...]) -> None:
        self._locations = {location.code: location for location in locations}

    def get(self, code: str) -> Location:
        if code not in self._locations:
            raise KeyError(f"Неизвестная локация: {code}")
        return self._locations[code]

    @property
    def all(self) -> list[Location]:
        return list(self._locations.values())
