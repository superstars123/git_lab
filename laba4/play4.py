from __future__ import annotations
from abstract_factory import HERO_CLASSES, WARRIOR
from facade import GameFacade
from game import Merchant, camp, show_expedition, show_hero, show_inventory


def play_lab4_game() -> None:
    game = GameFacade()
    print("\nЛАБОРАТОРНАЯ №4: RPG С НОВЫМИ ПАТТЕРНАМИ")
    name = input("Имя героя: ").strip()
    print("Выберите класс:")
    for number, hero_class in enumerate(HERO_CLASSES, 1):
        print(f"{number}. {hero_class.title}")
    class_choice = input("> ").strip()
    try:
        selected = HERO_CLASSES[int(class_choice) - 1]
        if int(class_choice) < 1:
            raise IndexError
    except (ValueError, IndexError):
        selected = WARRIOR
        print("Выбран класс Воин.")
    try:
        game.create_hero(name, selected.code)
    except ValueError as error:
        print(f"Ошибка создания героя: {error}")
        return

    merchant = Merchant(game.catalog)
    while True:
        hero = game.hero
        assert hero is not None
        show_hero(hero)
        print(f"Барьер: {hero.barrier_points} | Тактика: {game.tactic.title}")
        print("\n--- ИГРА (ЛАБА 4) ---")
        locations = game.registry.all
        for i, location in enumerate(locations, 1):
            print(f"{i}. {location.title} (уровень {location.recommended_level})")
        print("5. Лагерь и торговец")
        print("6. Посмотреть инвентарь")
        print("7. Сохранить героя (JSON + Proxy)")
        print("8. Загрузить героя")
        print("9. Выбрать тактику боя (Strategy)")
        print("10. Достижения и журнал (Observer)")
        print("0. Закончить игру")
        choice = input("> ").strip()
        try:
            if choice in ("1", "2", "3", "4"):
                report = game.explore(locations[int(choice) - 1].code)
                show_expedition(report)
                if not hero.is_alive():
                    print("Здоровье можно восстановить в лагере.")
            elif choice == "5":
                camp(hero, merchant)
            elif choice == "6":
                show_inventory(hero)
            elif choice == "7":
                game.save()
                print("Герой сохранён в saves.json (слот auto).")
            elif choice == "8":
                game.load()
                print("Герой успешно загружен, включая предметы и достижения.")
            elif choice == "9":
                print("1. Сбалансированная  2. Агрессивная  3. Осторожная")
                tactic_choice = {"1": "balanced", "2": "aggressive", "3": "cautious"}
                target = tactic_choice.get(input("> ").strip())
                if target is None:
                    print("Неизвестный вариант тактики.")
                else:
                    print("Новая тактика:", game.set_tactic(target).title)
            elif choice == "10":
                print("\nДостижения:")
                for achievement in sorted(game.achievements.unlocked):
                    print(" •", achievement)
                if not game.achievements.unlocked:
                    print("  Пока нет.")
                print("Журнал:")
                for line in game.journal.entries:
                    print(" •", line)
                if not game.journal.entries:
                    print("  Пока нет записей.")
            elif choice == "0":
                print("До встречи!")
                return
            else:
                print("Неизвестная команда.")
        except (ValueError, IndexError, KeyError, RuntimeError, OSError) as error:
            print("Не удалось выполнить действие:", error)
