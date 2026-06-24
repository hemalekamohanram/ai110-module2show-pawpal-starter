from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """A single care activity for a pet."""
    routine_name: str
    frequency: str        # e.g. "daily", "weekly"
    duration: int         # minutes
    priority: int         # 1 = low, 2 = medium, 3 = high
    completed: bool = False

    def get_routine_name(self) -> str:
        """Return the name of this care routine."""
        return self.routine_name

    def get_frequency(self) -> str:
        """Return how often this task recurs (e.g. 'daily', 'weekly')."""
        return self.frequency

    def get_duration(self) -> int:
        """Return how long this task takes in minutes."""
        return self.duration

    def get_priority(self) -> int:
        """Return the priority level (1 = low, 2 = medium, 3 = high)."""
        return self.priority

    def is_completed(self) -> bool:
        """Return True if this task has been marked complete."""
        return self.completed

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet with its own list of care tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """An owner who may have one or more pets."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Collect every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """
    The brain of PawPal+.
    Asks the Owner for all pet tasks, then selects and orders them
    into a daily plan that fits within available_time.
    """

    def __init__(self, owner: Owner, available_time: int) -> None:
        self.owner = owner
        self.available_time = available_time  # total minutes available in the day

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def generate(self) -> List[Task]:
        """
        Build a daily plan:
        1. Pull all tasks from the owner's pets.
        2. Sort by priority descending (3 = high scheduled first).
        3. Add tasks greedily until available_time is used up.
        """
        tasks = self.get_all_tasks()
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        plan: List[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration <= self.available_time:
                plan.append(task)
                time_used += task.duration

        return plan

    def get_total_duration(self, tasks: Optional[List[Task]] = None) -> int:
        """
        Sum durations of the given task list.
        If no list is passed, sums all tasks across all pets.
        """
        if tasks is None:
            tasks = self.get_all_tasks()
        return sum(t.get_duration() for t in tasks)
