from __future__ import annotations
from tempfile import TemporaryDirectory
from pathlib import Path
from abstract_factory import WARRIOR
from combat import Battle
from defense import create_defense_chain
from enemies import Goblin
from enemy_decorators import ArmoredEnemy, FrenziedEnemy
from events import AchievementObserver, EventBus, ExpeditionFinished
from facade import GameFacade
from hero import Hero
from prototype import create_catalog
from singleton import Dice
from storage import CachedSaveRepository, JsonSaveRepository
from tactics import AggressiveTactic, CautiousTactic
from weapon_adapter import HauntedWeapon


def demonstrate_lab4() -> None:
    Dice().reseed(42)
    catalog = create_catalog()
    print("\n===== LAB 4: СТРУКТУРНЫЕ И ПОВЕДЕНЧЕСКИЕ ПАТТЕРНЫ =====")

    print("\n1. DECORATOR / ДЕКОРАТОР")
    enemy = ArmoredEnemy(FrenziedEnemy(Goblin()))
    print(f"Комбинация 2 декораторов: {enemy.name}, HP {enemy.health}")

    print("\n2. PROXY / ЗАМЕСТИТЕЛЬ")
    with TemporaryDirectory() as directory:
        repository = CachedSaveRepository(JsonSaveRepository(Path(directory) / "saves.json"))
        repository.save("demo", {"value": 10})
        saved = repository.load("demo")
        print(f"JSON + кэш: {saved}; слоты: {repository.list_slots()}")

    print("\n3. ADAPTER / АДАПТЕР")
    adapted = HauntedWeapon(catalog.create_weapon("iron-sword"))
    print(f"Предмет стал врагом: {adapted.name}, HP {adapted.health}")

    print("\n4. FACADE / ФАСАД")
    with TemporaryDirectory() as directory:
        game = GameFacade(Path(directory) / "hero.json")
        hero = game.create_hero("Артур", "warrior")
        print(f"Фасад создал героя {hero.name} ({hero.hero_class.title})")
        game.save()
        game.load()
        print(f"Фасад сохранил и загрузил героя: {game.hero.name}")

        print("\n5. STRATEGY / СТРАТЕГИЯ")
        game.set_tactic("aggressive")
        print(f"Выбрана стратегия: {game.tactic.title}")
        game.set_tactic("cautious")
        print(f"Заменена в ходе игры: {game.tactic.title}")

        print("\n6. OBSERVER / НАБЛЮДАТЕЛЬ")
        report = game.explore("forest", seed=77)
        print("Экспедиция завершена:", "победа" if report.battle.victory else "поражение")
        print("Достижения:", ", ".join(sorted(game.achievements.unlocked)) or "пока нет")
        print("Записей в журнале:", len(game.journal.entries))

    print("\n7. CHAIN OF RESPONSIBILITY / ЦЕПОЧКА ОБЯЗАННОСТЕЙ")
    demo_hero = (Hero.Builder().set_name("Тест").set_class(WARRIOR)
                 .set_starter_kit(WARRIOR.starter_kit(catalog)).build())
    demo_hero.barrier_points = 8
    demo_hero.set_defense_chain(create_defense_chain(evasion_chance=0.0))
    suffered = demo_hero.receive_hit(30)
    print(f"30 входящего урона -> {suffered} по здоровью; "
          f"барьер остался {demo_hero.barrier_points}")

    print("\nВСЕ СЕМЬ ПАТТЕРНОВ ЛАБОРАТОРНОЙ №4 ПОКАЗАНЫ")


if __name__ == "__main__":
    demonstrate_lab4()
