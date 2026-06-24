from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Owner:
    name: str
    pet: Optional[Pet] = field(default=None)

    def get_name(self) -> str:
        return self.name

    def get_pet(self) -> Optional[Pet]:
        return self.pet


@dataclass
class Pet:
    name: str
    owner: Optional[Owner] = field(default=None)

    def get_name(self) -> str:
        return self.name

    def get_owner(self) -> Optional[Owner]:
        return self.owner


@dataclass
class Task:
    routine_name: str
    frequency: str   # e.g. "daily", "weekly"
    duration: int    # minutes
    priority: int    # 1 = low, 2 = medium, 3 = high

    def get_routine_name(self) -> str:
        return self.routine_name

    def get_frequency(self) -> str:
        return self.frequency

    def get_duration(self) -> int:
        return self.duration

    def get_priority(self) -> int:
        return self.priority


class Schedule:
    def __init__(self, pet: Pet, available_time: int) -> None:
        self.pet = pet
        self.tasks: List[Task] = []
        self.available_time = available_time  # total minutes available in the day

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        pass

    def get_schedule(self) -> List[Task]:
        """Return the current list of tasks."""
        pass

    def generate(self) -> List[Task]:
        """
        Build a daily plan by selecting and ordering tasks based on
        priority and available_time. Higher priority tasks should be
        scheduled first; tasks that exceed remaining time are skipped.
        """
        pass

    def get_total_duration(self) -> int:
        """Return the sum of durations for all tasks in the schedule."""
        pass
