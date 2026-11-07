from __future__ import annotations

"""Паттерн Prototype: предметы и каталог их копий."""
from copy import copy
from dataclasses import dataclass
from singleton import Dice
from combat import Hit

@dataclass(frozen=True)
class Enchantment:
    name: str
    bonus_damage: int = 0
    bonus_defense: float = 0.0

SHARP = Enchantment("Острое", bonus_damage=3)


FIERY = Enchantment("Огненное", bonus_damage=6)


STURDY = Enchantment("Прочное", bonus_defense=0.05)


class Item:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price
        self.enchantments: list[Enchantment] = []

    def copy(self) -> Item:
        # Поверхностная копия самого предмета + отдельная копия изменяемого списка.
        # Enchantment неизменяемый (frozen=True), поэтому его элементы можно разделять.
        clone = copy(self)
        clone.enchantments = list(self.enchantments)
        return clone

    def enchant(self, enchantment: Enchantment) -> None:
        self.enchantments.append(enchantment)

    def enchantment_names(self) -> str:
        return ", ".join(item.name for item in self.enchantments) or "нет"


class Weapon(Item):
    def __init__(self, name: str, price: int, damage: int,
                 min_damage: int | None = None, critical_chance: float = 0.0) -> None:
        super().__init__(name, price)
        self.base_damage = damage
        self.min_damage = min_damage if min_damage is not None else damage
        self.critical_chance = critical_chance

    @property
    def damage(self) -> int:
        return self.base_damage + sum(e.bonus_damage for e in self.enchantments)

    def roll_damage(self) -> Hit:
        dice = Dice()
        damage = dice.roll(self.min_damage, self.damage)
        critical = dice.chance(self.critical_chance)
        return Hit(damage * (2 if critical else 1), critical)

    def __str__(self) -> str:
        return f"{self.name} (урон {self.damage}, цена {self.price})"


class Armor(Item):
    def __init__(self, name: str, price: int, defense: float) -> None:
        super().__init__(name, price)
        self.base_defense = defense

    @property
    def defense(self) -> float:
        bonus = sum(e.bonus_defense for e in self.enchantments)
        return min(0.75, self.base_defense + bonus)

    def __str__(self) -> str:
        return f"{self.name} (защита {round(self.defense * 100)}%, цена {self.price})"


class ItemCatalog:
    def __init__(self) -> None:
        self._prototypes: dict[str, Item] = {}

    def register(self, code: str, prototype: Item) -> None:
        if code in self._prototypes:
            raise ValueError(f"Шаблон {code} уже зарегистрирован")
        self._prototypes[code] = prototype

    def create(self, code: str) -> Item:
        prototype = self._prototypes.get(code)
        if prototype is None:
            raise KeyError(f"Неизвестный предмет: {code}")
        return prototype.copy()

    def create_weapon(self, code: str) -> Weapon:
        item = self.create(code)
        if not isinstance(item, Weapon):
            raise TypeError(f"Предмет {code} не является оружием")
        return item

    def create_armor(self, code: str) -> Armor:
        item = self.create(code)
        if not isinstance(item, Armor):
            raise TypeError(f"Предмет {code} не является бронёй")
        return item

    @property
    def codes(self) -> list[str]:
        return list(self._prototypes)


def create_catalog() -> ItemCatalog:
    catalog = ItemCatalog()
    # Стартовое снаряжение
    catalog.register("training-sword", Weapon("Тренировочный меч", 20, 12))
    catalog.register("hunting-bow", Weapon("Охотничий лук", 20, 10, 7, 0.30))
    catalog.register("apprentice-staff", Weapon("Посох ученика", 20, 14, 8, 0.30))
    catalog.register("chainmail", Armor("Кольчуга", 40, 0.30))
    catalog.register("leather-armor", Armor("Кожаная броня", 30, 0.20))
    catalog.register("linen-robe", Armor("Льняная роба", 15, 0.10))
    # Товары торговца
    catalog.register("iron-sword", Weapon("Железный меч", 80, 17))
    catalog.register("elven-bow", Weapon("Эльфийский лук", 90, 14, 10, 0.40))
    catalog.register("ember-staff", Weapon("Тлеющий посох", 90, 20, 12, 0.30))
    catalog.register("plate-armor", Armor("Латы", 120, 0.40))
    # Добыча
    catalog.register("goblin-cleaver", Weapon("Гоблинский тесак", 40, 15))
    catalog.register("bone-bow", Weapon("Костяной лук", 140, 17, 12, 0.40))
    catalog.register("necromancer-staff", Weapon("Посох некроманта", 150, 25, 15, 0.35))
    catalog.register("knight-blade", Weapon("Клинок рыцаря", 150, 23))
    catalog.register("crypt-mail", Armor("Кольчуга стража склепа", 160, 0.45))
    catalog.register("dawn-blade", Weapon("Клинок рассвета", 500, 35))
    catalog.register("dragonscale-armor", Armor("Драконья чешуя", 500, 0.55))
    return catalog
