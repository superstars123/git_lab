from __future__ import annotations
from prototype import Item, Weapon, Armor, ItemCatalog, create_catalog
from abstract_factory import HERO_CLASSES, WARRIOR
from hero import Hero
from combat import BattleReport
from factory_method import ExpeditionReport, Forest, Crypt, DragonLair, LocationRegistry

class Merchant:
    SELL_PERCENT = 50

    def __init__(self, catalog: ItemCatalog,
                 assortment: tuple[str, ...] = ("iron-sword", "elven-bow", "ember-staff", "plate-armor")) -> None:
        self.catalog = catalog
        self.assortment = assortment

    def showcase(self) -> list[tuple[str, Item]]:
        return [(code, self.catalog.create(code)) for code in self.assortment]

    def buy(self, hero: Hero, code: str) -> Item:
        if code not in self.assortment:
            raise KeyError("Такого товара нет у торговца")
        item = self.catalog.create(code)
        hero.spend_gold(item.price)
        hero.add_item(item)
        return item

    def sell(self, hero: Hero, index: int) -> int:
        if not 0 <= index < len(hero.inventory):
            raise IndexError("Неверный номер предмета")
        item = hero.inventory.pop(index)
        price = item.price * self.SELL_PERCENT // 100
        hero.add_gold(price)
        return price


def show_hero(hero: Hero) -> None:
    print("\n" + "=" * 58)
    print(f"{hero.name} | {hero.hero_class.title} | уровень {hero.level}")
    print(f"Здоровье: {hero.health}/{hero.max_health} | опыт: {hero.experience}/{hero.experience_to_next_level}")
    print(f"Золото: {hero.gold}")
    print(f"Оружие: {hero.weapon}")
    print(f"Броня: {hero.armor}")
    print("=" * 58)


def show_battle(report: BattleReport) -> None:
    print(f"\nБой: {report.hero_name} против {report.enemy_name}")
    for event in report.events:
        extra = " КРИТИЧЕСКИЙ УДАР!" if event.critical else ""
        print(f"Раунд {event.round_number}: {event.attacker} наносит {event.damage} урона. "
              f"У {event.defender} осталось {event.defender_health} HP.{extra}")
        if event.death:
            print(f"{event.defender} повержен!")
    print("Победа!" if report.victory else "Поражение...")


def show_expedition(report: ExpeditionReport) -> None:
    print(f"\nЭкспедиция: {report.location_name}. Seed: {report.seed}")
    show_battle(report.battle)
    reward = report.rewards
    if reward.gold >= 0:
        print(f"Награда: опыт +{reward.experience}, золото +{reward.gold}")
    else:
        print(f"Штраф: потеряно золота {-reward.gold}")
    if reward.levels_gained:
        print(f"Новый уровень! Получено уровней: {reward.levels_gained}")
    if reward.loot:
        print(f"Найдена добыча: {reward.loot.name}; зачарования: {reward.loot.enchantment_names()}")
    elif reward.gold >= 0:
        print("Добыча не найдена.")


def show_inventory(hero: Hero) -> None:
    print("\nИнвентарь:")
    if not hero.inventory:
        print("  Пусто")
        return
    for i, item in enumerate(hero.inventory, 1):
        print(f"  {i}. {item} | зачарования: {item.enchantment_names()}")


def camp(hero: Hero, merchant: Merchant) -> None:
    while True:
        print("\n--- ЛАГЕРЬ ---")
        print("1. Отдохнуть и восстановить здоровье")
        print("2. Посмотреть инвентарь")
        print("3. Надеть предмет из инвентаря")
        print("4. Купить предмет")
        print("5. Продать предмет")
        print("0. Назад")
        command = input("> ").strip()
        try:
            if command == "1":
                hero.restore_health()
                print("Здоровье полностью восстановлено.")
            elif command == "2":
                show_inventory(hero)
            elif command == "3":
                show_inventory(hero)
                if hero.inventory:
                    index = int(input("Номер предмета, который надеть: ")) - 1
                    equipped = hero.equip(index)
                    print(f"Надет предмет: {equipped.name}. Снятое снаряжение отправлено в инвентарь.")
            elif command == "4":
                print("\nТовары торговца:")
                for i, (code, item) in enumerate(merchant.showcase(), 1):
                    print(f"{i}. {item}")
                number = int(input("Номер товара (0 — отмена): "))
                if number:
                    code = merchant.assortment[number - 1]
                    item = merchant.buy(hero, code)
                    print(f"Куплено: {item.name}")
            elif command == "5":
                show_inventory(hero)
                if hero.inventory:
                    number = int(input("Номер предмета для продажи (0 — отмена): "))
                    if number:
                        price = merchant.sell(hero, number - 1)
                        print(f"Предмет продан за {price} золота.")
            elif command == "0":
                return
            else:
                print("Неизвестная команда.")
        except (ValueError, IndexError, KeyError) as error:
            print(f"Не удалось выполнить действие: {error}")


def play_game() -> None:
    catalog = create_catalog()
    print("Добро пожаловать! Герой разбил лагерь у мистического леса.")
    name = input("Имя героя: ").strip()
    print("\nВыберите класс:")
    for i, hero_class in enumerate(HERO_CLASSES, 1):
        print(f"{i}. {hero_class.title} (здоровье {hero_class.base_health})")
    try:
        choice = int(input("> "))
        if not 1 <= choice <= len(HERO_CLASSES):
            raise ValueError
        hero_class = HERO_CLASSES[choice - 1]
    except ValueError:
        print("Некорректный выбор, выбран Воин.")
        hero_class = WARRIOR

    kit = hero_class.starter_kit(catalog)
    hero = (Hero.Builder().set_name(name).set_class(hero_class)
            .set_starter_kit(kit).build())
    merchant = Merchant(catalog)
    registry = LocationRegistry((Forest(catalog), Crypt(catalog), DragonLair(catalog)))

    while True:
        show_hero(hero)
        print("\nКуда отправиться?")
        for i, location in enumerate(registry.all, 1):
            print(f"{i}. {location.title} (рекомендуемый уровень: {location.recommended_level})")
        print("4. Лагерь")
        print("5. Инвентарь")
        print("0. Выйти из игры")
        command = input("> ").strip()
        try:
            if command in ("1", "2", "3"):
                location = registry.all[int(command) - 1]
                report = location.explore(hero)
                show_expedition(report)
                if not hero.is_alive():
                    print("Герой пал. Вернитесь в лагерь, чтобы восстановиться.")
                    # Восстановление доступно через лагерь даже после поражения.
            elif command == "4":
                camp(hero, merchant)
            elif command == "5":
                show_inventory(hero)
            elif command == "0":
                print("Экспедиция окончена. До встречи!")
                break
            else:
                print("Неизвестная команда.")
        except (ValueError, IndexError, KeyError) as error:
            print(f"Ошибка: {error}")


# Игровой режим 4-й лабораторной; отдельный play4.py не нужен.
def play_lab4_game() -> None:
    from facade import GameFacade
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



def main() -> None:
    print("ЛАБОРАТОРНЫЕ РАБОТЫ №3 И №4 — ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ")
    print("1. Демонстрация паттернов лабораторной №3")
    print("2. Запустить исходную текстовую RPG (лаба 3)")
    print("3. Демонстрация семи паттернов лабораторной №4")
    print("4. Запустить RPG с новыми паттернами (лаба 4)")
    from demo import Demo
    choice = input("> ").strip()
    if choice == "2":
        play_game()
    elif choice == "3":
        Demo.run_lab4()
    elif choice == "4":
        play_lab4_game()
    else:
        Demo.run_lab3()


if __name__ == "__main__":
    main()
