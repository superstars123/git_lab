from __future__ import annotations
import random

class Dice:
    _instance: Dice | None = None

    def __new__(cls) -> Dice:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._random = random.Random()
        return cls._instance

    def reseed(self, seed: int) -> None:
        """Устанавливает seed, чтобы можно было повторить последовательность бросков."""
        self._random.seed(seed)

    def next_seed(self) -> int:
        return self._random.randint(0, 999_999)

    def roll(self, low: int, high: int) -> int:
        return self._random.randint(low, high)

    def chance(self, probability: float) -> bool:
        return self._random.random() < probability

    def pick(self, values: tuple[str, ...] | list[str]):
        if not values:
            raise ValueError("Нельзя выбрать элемент из пустого списка")
        return self._random.choice(values)

