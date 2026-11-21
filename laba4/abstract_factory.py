from __future__ import annotations
from abc import ABC, abstractmethod
from prototype import Weapon, Armor, ItemCatalog

class StarterKitFactory(ABC):
    @abstractmethod
    def create_weapon(self) -> Weapon: ...

    @abstractmethod
    def create_armor(self) -> Armor: ...


class WarriorKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog) -> None:
        self.catalog = catalog

    def create_weapon(self) -> Weapon:
        return self.catalog.create_weapon("training-sword")

    def create_armor(self) -> Armor:
        return self.catalog.create_armor("chainmail")


class RangerKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog) -> None:
        self.catalog = catalog

    def create_weapon(self) -> Weapon:
        return self.catalog.create_weapon("hunting-bow")

    def create_armor(self) -> Armor:
        return self.catalog.create_armor("leather-armor")


class MageKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog) -> None:
        self.catalog = catalog

    def create_weapon(self) -> Weapon:
        return self.catalog.create_weapon("apprentice-staff")

    def create_armor(self) -> Armor:
        return self.catalog.create_armor("linen-robe")


class HeroClass:
    def __init__(self, code: str, title: str, base_health: int,
                 factory_type: type[StarterKitFactory]) -> None:
        self.code = code
        self.title = title
        self.base_health = base_health
        self.factory_type = factory_type

    def starter_kit(self, catalog: ItemCatalog) -> StarterKitFactory:
        return self.factory_type(catalog)

WARRIOR = HeroClass("warrior", "Воин", 120, WarriorKitFactory)


RANGER = HeroClass("ranger", "Следопыт", 100, RangerKitFactory)


MAGE = HeroClass("mage", "Маг", 85, MageKitFactory)


HERO_CLASSES = (WARRIOR, RANGER, MAGE)


