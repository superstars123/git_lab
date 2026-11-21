from __future__ import annotations
from prototype import create_catalog, FIERY
from abstract_factory import HERO_CLASSES, WARRIOR
from hero import Hero
from singleton import Dice
from factory_method import Forest, Crypt, DragonLair


class Demo:

    @staticmethod
    def run_lab3() -> None:
        catalog = create_catalog()
        Dice().reseed(7)

        print("===== 1. SINGLETON / ОДИНОЧКА =====")
        first = Dice()
        second = Dice()
        print("Первый объект:", first)
        print("Второй объект:", second)
        print("Это один и тот же объект:", first is second)

        print("\n===== 2. PROTOTYPE / ПРОТОТИП =====")
        original = catalog.create_weapon("training-sword")
        modified_copy = catalog.create_weapon("training-sword")
        modified_copy.enchant(FIERY)
        another_copy = catalog.create_weapon("training-sword")
        print("Исходный шаблон-копия:", original, "| зачарования:", original.enchantment_names())
        print("Изменённая копия:", modified_copy, "| зачарования:", modified_copy.enchantment_names())
        print("Ещё одна копия:", another_copy, "| зачарования:", another_copy.enchantment_names())
        print("Копии — разные объекты:", original is not modified_copy)
        print("Изменение одной копии не затронуло другую:", original.damage == another_copy.damage)

        print("\n===== 3. ABSTRACT FACTORY / АБСТРАКТНАЯ ФАБРИКА =====")
        for hero_class in HERO_CLASSES:
            factory = hero_class.starter_kit(catalog)
            weapon = factory.create_weapon()
            armor = factory.create_armor()
            print(f"Фабрика {hero_class.title} создала семейство: {weapon.name} + {armor.name}")

        print("\n===== 4. BUILDER / СТРОИТЕЛЬ =====")
        factory = WARRIOR.starter_kit(catalog)
        hero = (Hero.Builder().set_name("Артур").set_class(WARRIOR)
                .set_starter_kit(factory).set_level(2).set_gold(75).build())
        print(f"Создан герой: {hero.name}; класс: {hero.hero_class.title}; уровень: {hero.level};")
        print(f"здоровье: {hero.health}/{hero.max_health}; золото: {hero.gold};")
        print(f"оружие: {hero.weapon}; броня: {hero.armor}")

        print("\n===== 5. FACTORY METHOD / ФАБРИЧНЫЙ МЕТОД =====")
        for location in (Forest(catalog), Crypt(catalog), DragonLair(catalog)):
            enemy = location.create_enemy()
            print(f"{location.title} создала врага: {enemy.name}; HP: {enemy.max_health}")


    @staticmethod
    def run_lab4() -> None:
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from combat import Battle
        from defense import create_defense_chain
        from enemies import Goblin
        from enemy_decorators import ArmoredEnemy, FrenziedEnemy
        from events import AchievementObserver, EventBus, ExpeditionFinished
        from facade import GameFacade
        from storage import CachedSaveRepository, JsonSaveRepository
        from tactics import AggressiveTactic, CautiousTactic
        from weapon_adapter import HauntedWeapon
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

    @staticmethod
    def run() -> None:
        """Демонстрация всех паттернов одним запуском."""
        Demo.run_lab3()
        Demo.run_lab4()


if __name__ == "__main__":
    Demo.run()
