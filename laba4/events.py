from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from factory_method import ExpeditionReport


@dataclass(frozen=True)
class ExpeditionFinished:
    report: ExpeditionReport


class EventListener(Protocol):
    def update(self, event: ExpeditionFinished) -> None: ...


class EventBus:
    def __init__(self) -> None:
        self._listeners: list[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: EventListener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def publish(self, event: ExpeditionFinished) -> None:
        for listener in tuple(self._listeners):
            listener.update(event)


class AchievementObserver:
    def __init__(self) -> None:
        self.unlocked: set[str] = set()

    def update(self, event: ExpeditionFinished) -> None:
        report = event.report
        if report.battle.victory:
            self.unlocked.add("Первая победа")
        else:
            self.unlocked.add("Не сдавайся")
        if "дракона" in report.location_name.lower() and report.battle.victory:
            self.unlocked.add("Победитель дракона")
        if report.rewards.levels_gained:
            self.unlocked.add("Новый уровень")
        if report.rewards.loot is not None:
            self.unlocked.add("Искатель сокровищ")


class JournalObserver:
    def __init__(self) -> None:
        self.entries: list[str] = []

    def update(self, event: ExpeditionFinished) -> None:
        report = event.report
        status = "победа" if report.battle.victory else "поражение"
        self.entries.append(
            f"{report.location_name}: {status}, опыт {report.rewards.experience}, "
            f"золото {report.rewards.gold}, seed {report.seed}"
        )
