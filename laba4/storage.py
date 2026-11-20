from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
import json
from pathlib import Path


class SaveRepository(ABC):
    @abstractmethod
    def save(self, slot: str, payload: dict) -> None: ...

    @abstractmethod
    def load(self, slot: str) -> dict: ...

    @abstractmethod
    def list_slots(self) -> list[str]: ...


class JsonSaveRepository(SaveRepository):
    def __init__(self, path: str | Path = "saves.json") -> None:
        self.path = Path(path)

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Некорректный формат файла сохранений")
        return data

    def save(self, slot: str, payload: dict) -> None:
        if not slot:
            raise ValueError("Название слота не может быть пустым")
        data = self._read_all()
        data[slot] = deepcopy(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        temporary.replace(self.path)

    def load(self, slot: str) -> dict:
        data = self._read_all()
        if slot not in data:
            raise KeyError(f"Сохранение '{slot}' не найдено")
        return deepcopy(data[slot])

    def list_slots(self) -> list[str]:
        return sorted(self._read_all())


class CachedSaveRepository(SaveRepository):
    def __init__(self, real_repository: SaveRepository) -> None:
        self.real_repository = real_repository
        self._cache: dict[str, dict] = {}

    def save(self, slot: str, payload: dict) -> None:
        self.real_repository.save(slot, payload)
        self._cache[slot] = deepcopy(payload)

    def load(self, slot: str) -> dict:
        if slot not in self._cache:
            self._cache[slot] = self.real_repository.load(slot)
        return deepcopy(self._cache[slot])

    def list_slots(self) -> list[str]:
        return self.real_repository.list_slots()
