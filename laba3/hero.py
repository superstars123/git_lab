from __future__ import annotations

"""Паттерн Builder и модель героя."""
from combat import Combatant, Hit
from prototype import Item, Weapon, Armor
from abstract_factory import HeroClass, StarterKitFactory

class Hero(Combatant):
    MAX_NAME_LENGTH = 20
    STARTING_GOLD = 50
    HEALTH_PER_LEVEL = 15
    DAMAGE_PER_LEVEL = 3
    EXPERIENCE_PER_LEVEL = 100

    def __init__(self, builder: Hero.Builder) -> None:
        self._name = builder.name or ""
        self.hero_class = builder.hero_class
        self.weapon = builder.weapon
        self.armor = builder.armor
        self.level = builder.level
        self.experience = 0
        self.gold = builder.gold
        self.inventory: list[Item] = []
        self._max_health = self.hero_class.base_health + (self.level - 1) * self.HEALTH_PER_LEVEL
        self._health = self._max_health

    class Builder:
        def __init__(self) -> None:
            self.name: str | None = None
            self.hero_class: HeroClass | None = None
            self.weapon: Weapon | None = None
            self.armor: Armor | None = None
            self.level = 1
            self.gold = Hero.STARTING_GOLD

        def set_name(self, name: str) -> Hero.Builder:
            self.name = name.strip()
            return self

        def set_class(self, hero_class: HeroClass) -> Hero.Builder:
            self.hero_class = hero_class
            return self

        def set_starter_kit(self, factory: StarterKitFactory) -> Hero.Builder:
            self.weapon = factory.create_weapon()
            self.armor = factory.create_armor()
            return self

        def set_weapon(self, weapon: Weapon) -> Hero.Builder:
            self.weapon = weapon
            return self

        def set_armor(self, armor: Armor) -> Hero.Builder:
            self.armor = armor
            return self

        def set_level(self, level: int) -> Hero.Builder:
            self.level = level
            return self

        def set_gold(self, gold: int) -> Hero.Builder:
            self.gold = gold
            return self

        def build(self) -> Hero:
            if not self.name:
                raise ValueError("У героя должно быть имя")
            if len(self.name) > Hero.MAX_NAME_LENGTH:
                raise ValueError(f"Имя не может быть длиннее {Hero.MAX_NAME_LENGTH} символов")
            if self.hero_class is None:
                raise ValueError("Не выбран класс героя")
            if self.weapon is None or self.armor is None:
                raise ValueError("Герою нужны оружие и броня")
            if self.level < 1:
                raise ValueError("Уровень должен быть не меньше 1")
            if self.gold < 0:
                raise ValueError("Количество золота не может быть отрицательным")
            return Hero(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._max_health

    @property
    def experience_to_next_level(self) -> int:
        return self.EXPERIENCE_PER_LEVEL

    def roll_damage(self) -> Hit:
        hit = self.weapon.roll_damage()
        bonus = (self.level - 1) * self.DAMAGE_PER_LEVEL
        return Hit(hit.damage + bonus, hit.critical)

    def receive_hit(self, damage: int) -> int:
        actual = max(1, round(damage * (1 - self.armor.defense)))
        self._health = max(0, self._health - actual)
        return actual

    def restore_health(self) -> None:
        self._health = self._max_health

    def gain_experience(self, amount: int) -> int:
        self.experience += amount
        levels_gained = 0
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            levels_gained += 1
        if levels_gained:
            self._max_health = self.hero_class.base_health + (self.level - 1) * self.HEALTH_PER_LEVEL
            self.restore_health()
        return levels_gained

    def add_gold(self, amount: int) -> None:
        self.gold += amount

    def spend_gold(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Нельзя потратить отрицательное количество золота")
        if amount > self.gold:
            raise ValueError(f"Не хватает золота: нужно {amount}, есть {self.gold}")
        self.gold -= amount

    def add_item(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_item(self, item: Item) -> None:
        if item not in self.inventory:
            raise ValueError("Этого предмета нет в инвентаре")
        self.inventory.remove(item)

    def equip(self, index: int) -> Item:
        if not 0 <= index < len(self.inventory):
            raise IndexError("Неверный номер предмета")
        item = self.inventory.pop(index)
        if isinstance(item, Weapon):
            old = self.weapon
            self.weapon = item
        elif isinstance(item, Armor):
            old = self.armor
            self.armor = item
        else:
            self.inventory.insert(index, item)
            raise TypeError("Неизвестный тип предмета")
        self.inventory.append(old)
        return item

