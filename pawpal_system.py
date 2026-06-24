from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum
from typing import List, Optional

# Maps a frequency string to the number of days until the next occurrence.
FREQUENCY_DAYS: dict[str, int] = {"daily": 1, "weekly": 7}


class Priority(IntEnum):
    """Named priority levels. IntEnum means Priority.HIGH == 3 stays True."""
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3


@dataclass
class Task:
    """A single care activity for a pet."""
    routine_name: str
    frequency: str        # e.g. "daily", "weekly"
    duration: int         # minutes
    priority: int         # 1 = low, 2 = medium, 3 = high
    completed: bool = False
    start_time: Optional[str] = None   # "HH:MM" format, e.g. "08:30"
    due_date: Optional[date] = None    # calendar date this occurrence is due

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

    def next_occurrence(self) -> Optional[Task]:
        """
        Return a fresh, uncompleted copy of this task scheduled for the next
        due date, calculated with timedelta:
          - "daily"  → due_date + 1 day
          - "weekly" → due_date + 7 days
        Returns None for frequencies not in FREQUENCY_DAYS (e.g. one-off tasks).
        """
        interval = FREQUENCY_DAYS.get(self.frequency)
        if interval is None:
            return None
        base = self.due_date if self.due_date is not None else date.today()
        return Task(
            routine_name=self.routine_name,
            frequency=self.frequency,
            duration=self.duration,
            priority=self.priority,
            completed=False,
            start_time=self.start_time,
            due_date=base + timedelta(days=interval),
        )

    def to_dict(self) -> dict:
        """Serialize this task to a JSON-safe dictionary."""
        return {
            "routine_name": self.routine_name,
            "frequency":    self.frequency,
            "duration":     self.duration,
            "priority":     self.priority,
            "completed":    self.completed,
            "start_time":   self.start_time,
            "due_date":     self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Reconstruct a Task from a dictionary (e.g. loaded from JSON)."""
        return cls(
            routine_name=data["routine_name"],
            frequency=data["frequency"],
            duration=data["duration"],
            priority=data["priority"],
            completed=data.get("completed", False),
            start_time=data.get("start_time"),
            due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        )


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

    def to_dict(self) -> dict:
        """Serialize this pet and all its tasks to a dictionary."""
        return {
            "name":    self.name,
            "species": self.species,
            "tasks":   [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Reconstruct a Pet (and its tasks) from a dictionary."""
        pet = cls(name=data["name"], species=data["species"])
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


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

    def to_dict(self) -> dict:
        """Serialize this owner and all their pets/tasks to a dictionary."""
        return {
            "name": self.name,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Reconstruct an Owner (pets + tasks) from a dictionary."""
        owner = cls(name=data["name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner


def save_to_json(owner: Owner, filepath: str = "data.json") -> None:
    """Write the owner's full data tree to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(owner.to_dict(), f, indent=2)


def load_from_json(filepath: str = "data.json") -> Optional[Owner]:
    """
    Load an Owner from a JSON file.
    Returns None if the file does not exist yet.
    """
    if not os.path.exists(filepath):
        return None
    with open(filepath) as f:
        return Owner.from_dict(json.load(f))


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
        2. Sort by priority descending; when priorities are equal, sort by
           start_time ascending so earlier-timed tasks come first.
        3. Add tasks greedily until available_time is used up.
        """
        tasks = self.get_all_tasks()
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (-t.priority, t.start_time if t.start_time else "99:99")
        )

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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Return a new list of tasks sorted chronologically by start_time.

        How it works:
          - start_time is stored as a zero-padded "HH:MM" string (e.g. "08:30").
          - Zero-padding means lexicographic order is identical to chronological
            order, so Python's built-in sorted() with a plain string key is
            sufficient — no datetime parsing needed.
          - The lambda uses "99:99" as a sentinel for tasks that have no
            start_time yet, placing them at the end of the sorted list rather
            than raising a TypeError from comparing None to a string.

        Args:
            tasks: the list of Task objects to sort (not mutated).

        Returns:
            A new list with the same tasks in ascending time order.
        """
        return sorted(
            tasks,
            key=lambda t: t.start_time if t.start_time is not None else "99:99"
        )

    def filter_by_status(self, completed: bool) -> List[Task]:
        """
        Return all tasks across every pet whose completion status matches
        the given flag.

        How it works:
          - Calls get_all_tasks() to collect tasks from every pet in one flat
            list, then filters with a list comprehension in a single O(n) pass.
          - Delegates to Task.is_completed() rather than reading the field
            directly, keeping the filter decoupled from the dataclass internals.

        Args:
            completed: pass False to get pending (not yet done) tasks;
                       pass True to get tasks that have been marked complete.

        Returns:
            A new list containing only the tasks whose completed flag equals
            the given value. Returns an empty list if none match.
        """
        return [t for t in self.get_all_tasks() if t.is_completed() == completed]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """
        Return all tasks assigned to the named pet.

        How it works:
          - Iterates the owner's pet list and returns early on the first name
            match, so it never scans more pets than necessary (short-circuit).
          - Name comparison is case-sensitive and exact — "Mochi" and "mochi"
            are treated as different pets.
          - Returns the pet's live task list (not a copy), so callers see any
            tasks added after this call without re-filtering.

        Args:
            pet_name: the exact name of the pet to look up.

        Returns:
            The List[Task] belonging to that pet, or an empty list if no pet
            with that name exists under this owner.
        """
        for pet in self.owner.get_pets():
            if pet.get_name() == pet_name:
                return pet.get_tasks()
        return []

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """
        Lightweight O(n) conflict detection.

        Strategy — one pass, one dict:
          1. Walk every task and group them by start_time into a dict.
          2. Any slot that collected more than one task is a conflict.
          3. Return human-readable warning strings; never raise an exception.

        Tasks without a start_time are skipped — they haven't been placed on
        the timeline yet so there is nothing to conflict with.

        Pass an explicit task list to check a subset (e.g. a generated plan),
        or omit it to check every task across all pets.
        """
        if tasks is None:
            tasks = self.get_all_tasks()

        # Dict comprehension: build task-id → pet name in one readable expression.
        # Using id(t) as the key avoids false matches between tasks whose fields
        # happen to be identical.
        task_to_pet = {
            id(t): pet.get_name()
            for pet in self.owner.get_pets()
            for t in pet.get_tasks()
        }

        # defaultdict(list) is the standard Python pattern for grouping —
        # cleaner than setdefault(..., []).append(...).
        slot_map: defaultdict[str, list[str]] = defaultdict(list)
        for task in tasks:
            if task.start_time is None:
                continue
            pet_label = task_to_pet.get(id(task), "unknown pet")
            slot_map[task.start_time].append(
                f"{task.get_routine_name()} ({pet_label})"
            )

        # Explicit loop kept here (AI suggested a list comprehension, but
        # combining filter + format + sort into one expression hurt readability).
        warnings: List[str] = []
        for slot, names in sorted(slot_map.items()):
            if len(names) > 1:
                clashing = " vs. ".join(names)
                warnings.append(
                    f"WARNING: Scheduling conflict at {slot} — {clashing}"
                )
        return warnings

    def weighted_sort(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sort tasks by a score that combines priority AND urgency.

        Score = priority × urgency_factor, where:
          urgency_factor = 1 + 1 / (days_until_due + 1)   (when due_date is set)
          urgency_factor = 1.0                              (no due_date → plain priority)

        Examples at priority 3:
          due today      → score 3 × (1 + 1/1) = 6.0
          due in 6 days  → score 3 × (1 + 1/7) ≈ 3.43
          no due_date    → score 3 × 1.0        = 3.0

        A high-priority task due today will always beat the same task due next week.
        A medium-priority task due today can outrank a high-priority task with no due_date.
        """
        if tasks is None:
            tasks = self.get_all_tasks()
        today = date.today()

        def score(task: Task) -> float:
            if task.due_date is not None:
                days_away = max(0, (task.due_date - today).days)
                urgency = 1 + 1 / (days_away + 1)
            else:
                urgency = 1.0
            return task.priority * urgency

        return sorted(tasks, key=score, reverse=True)

    def weighted_generate(self) -> List[Task]:
        """
        Like generate(), but uses weighted_sort() instead of plain priority sort.
        Tasks due sooner are scheduled first when priority is equal.
        """
        sorted_tasks = self.weighted_sort()
        plan: List[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration <= self.available_time:
                plan.append(task)
                time_used += task.duration
        return plan

    def mark_task_complete(self, task: Task, pet: Pet) -> Optional[Task]:
        """
        Mark a task done and auto-schedule its next occurrence.

        Steps:
          1. Call task.mark_complete() to flip completed → True.
          2. Call task.next_occurrence() which uses timedelta to build a
             fresh Task due in 1 day (daily) or 7 days (weekly).
          3. If a next occurrence exists, add it to the pet's task list.

        Returns the newly created Task, or None if the task doesn't recur.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task
