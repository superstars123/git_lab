from __future__ import annotations
from abstract_factory import HERO_CLASSES
from hero import Hero
from prototype import Armor, Enchantment, Item, Weapon


def item_to_data(item: Item) -> dict:
    result = {
        "kind": "weapon" if isinstance(item, Weapon) else "armor",
        "name": item.name,
        "price": item.price,
        "enchantments": [
            {"name": e.name, "bonus_damage": e.bonus_damage,
             "bonus_defense": e.bonus_defense}
            for e in item.enchantments
        ],
    }
    if isinstance(item, Weapon):
        result.update(base_damage=item.base_damage, min_damage=item.min_damage,
                      critical_chance=item.critical_chance)
    elif isinstance(item, Armor):
        result["base_defense"] = item.base_defense
    else:
        raise TypeError(f"Неизвестный тип предмета: {type(item)}")
    return result


def item_from_data(data: dict) -> Item:
    if data["kind"] == "weapon":
        item = Weapon(data["name"], data["price"], data["base_damage"],
                      data["min_damage"], data["critical_chance"])
    elif data["kind"] == "armor":
        item = Armor(data["name"], data["price"], data["base_defense"])
    else:
        raise ValueError("Неизвестный тип предмета в сохранении")
    for entry in data.get("enchantments", []):
        item.enchant(Enchantment(entry["name"], entry["bonus_damage"],
                                 entry["bonus_defense"]))
    return item


def hero_to_data(hero: Hero) -> dict:
    return {
        "name": hero.name,
        "class": hero.hero_class.code,
        "level": hero.level,
        "experience": hero.experience,
        "gold": hero.gold,
        "health": hero.health,
        "barrier_points": hero.barrier_points,
        "weapon": item_to_data(hero.weapon),
        "armor": item_to_data(hero.armor),
        "inventory": [item_to_data(item) for item in hero.inventory],
    }


def hero_from_data(data: dict) -> Hero:
    hero_class = next((c for c in HERO_CLASSES if c.code == data["class"]), None)
    if hero_class is None:
        raise ValueError("Неизвестный класс героя в сохранении")
    weapon = item_from_data(data["weapon"])
    armor = item_from_data(data["armor"])
    if not isinstance(weapon, Weapon) or not isinstance(armor, Armor):
        raise ValueError("Некорректное снаряжение героя в сохранении")
    hero = (Hero.Builder().set_name(data["name"]).set_class(hero_class)
            .set_weapon(weapon).set_armor(armor)
            .set_level(data["level"]).set_gold(data["gold"]).build())
    hero.experience = data["experience"]
    if not 0 <= data["health"] <= hero.max_health:
        raise ValueError("Некорректное значение здоровья в сохранении")
    hero._health = data["health"]
    hero.barrier_points = data.get("barrier_points", 0)
    if hero.barrier_points < 0:
        raise ValueError("Некорректное значение барьера в сохранении")
    hero.inventory = [item_from_data(item) for item in data["inventory"]]
    return hero
