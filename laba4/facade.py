from __future__ import annotations
from abc import ABC
from pathlib import Path
from abstract_factory import HERO_CLASSES
from defense import create_defense_chain
from enemy_decorators import ArmoredEnemy, FrenziedEnemy, LegendaryEnemy
from events import AchievementObserver, EventBus, ExpeditionFinished, JournalObserver
from factory_method import (Crypt, DragonLair, ExpeditionReport, Forest,
                            HauntedArmory, LocationRegistry)
from hero import Hero
from prototype import create_catalog
from serialization import hero_from_data, hero_to_data
from storage import CachedSaveRepository, JsonSaveRepository, SaveRepository
from tactics import BalancedTactic, BattleTactic, TACTICS


class GameFacade:
    def __init__(self, save_file: str | Path = "saves.json",
                 repository: SaveRepository | None = None) -> None:
        self.catalog = create_catalog()
        self.registry = LocationRegistry((Forest(self.catalog), Crypt(self.catalog),
                                          DragonLair(self.catalog), HauntedArmory(self.catalog)))
        self.repository = CachedSaveRepository(repository or JsonSaveRepository(save_file))
        self.events = EventBus()
        self.achievements = AchievementObserver()
        self.journal = JournalObserver()
        self.events.subscribe(self.achievements)
        self.events.subscribe(self.journal)
        self.hero: Hero | None = None
        self.tactic: BattleTactic = BalancedTactic()

    def create_hero(self, name: str, class_code: str) -> Hero:
        hero_class = next((c for c in HERO_CLASSES if c.code == class_code), None)
        if hero_class is None:
            raise ValueError(f"Неизвестный класс героя: {class_code}")
        kit = hero_class.starter_kit(self.catalog)
        self.hero = (Hero.Builder().set_name(name).set_class(hero_class)
                     .set_starter_kit(kit).build())
        self._setup_hero_defense(self.hero)
        self.achievements.unlocked.clear()
        self.journal.entries.clear()
        return self.hero

    def _setup_hero_defense(self, hero: Hero) -> None:
        hero.set_defense_chain(create_defense_chain())
        # Initial barrier is given only for a new hero.
        if hero.barrier_points == 0:
            hero.barrier_points = 8

    def set_tactic(self, code: str) -> BattleTactic:
        if code not in TACTICS:
            raise ValueError(f"Неизвестная тактика: {code}")
        self.tactic = TACTICS[code]()
        return self.tactic

    def explore(self, location_code: str, seed: int | None = None) -> ExpeditionReport:
        if self.hero is None:
            raise RuntimeError("Сначала создайте или загрузите героя")
        location = self.registry.get(location_code)
        # The decorators apply to enemies created by the ORIGINAL factory method.
        decorators = {
            "forest": (FrenziedEnemy,),
            "crypt": (ArmoredEnemy,),
            "dragon-lair": (LegendaryEnemy,),
            "haunted-armory": (ArmoredEnemy, FrenziedEnemy),
        }[location_code]
        report = location.explore(self.hero, seed=seed,
                                  tactic=self.tactic, enemy_decorators=decorators)
        self.events.publish(ExpeditionFinished(report))
        return report

    def save(self, slot: str = "auto") -> None:
        if self.hero is None:
            raise RuntimeError("Нечего сохранять: герой ещё не создан")
        self.repository.save(slot, {
            "hero": hero_to_data(self.hero),
            "tactic": next((key for key, value in TACTICS.items()
                            if isinstance(self.tactic, value)), "balanced"),
            "achievements": sorted(self.achievements.unlocked),
            "journal": list(self.journal.entries),
        })

    def load(self, slot: str = "auto") -> Hero:
        payload = self.repository.load(slot)
        self.hero = hero_from_data(payload["hero"])
        # Must not reset saved barrier points when loading a saved character.
        self.hero.set_defense_chain(create_defense_chain())
        self.set_tactic(payload.get("tactic", "balanced"))
        self.achievements.unlocked = set(payload.get("achievements", []))
        self.journal.entries = list(payload.get("journal", []))
        return self.hero
