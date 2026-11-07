from __future__ import annotations

"""Игровой процесс, лагерь, торговец и демонстрация паттернов."""
from prototype import Item, Weapon, Armor, ItemCatalog, create_catalog, FIERY
from abstract_factory import HERO_CLASSES, WARRIOR
from hero import Hero
from singleton import Dice
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


def demonstrate_patterns() -> None:
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
    # У каждой фабрики два метода: создать оружие и создать броню.
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
    # Минимум два подкласса. Здесь показаны все три локации.
    for location in (Forest(catalog), Crypt(catalog), DragonLair(catalog)):
        enemy = location.create_enemy()
        print(f"{location.title} создала врага: {enemy.name}; HP: {enemy.max_health}")


def main() -> None:
    print("ЛАБОРАТОРНАЯ РАБОТА №3 — ПОРОЖДАЮЩИЕ ПАТТЕРНЫ")
    print("1. Демонстрация паттернов (для защиты)")
    print("2. Запустить текстовую RPG")
    choice = input("> ").strip()
    if choice == "2":
        play_game()
    else:
        demonstrate_patterns()

if __name__ == "__main__":
    main()
