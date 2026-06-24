from datetime import date
from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# --- Priority emoji + label helpers ---
PRIORITY_ICON  = {Priority.LOW: "🟢", Priority.MEDIUM: "🟡", Priority.HIGH: "🔴"}
PRIORITY_LABEL = {Priority.LOW: "low", Priority.MEDIUM: "medium", Priority.HIGH: "high"}
SPECIES_ICON   = {"cat": "🐱", "dog": "🐶", "other": "🐾"}

# --- Setup ---
owner = Owner(name="Jordan")

mochi   = Pet(name="Mochi",   species="cat")
biscuit = Pet(name="Biscuit", species="dog")

# Tasks for Mochi — same HIGH priority, different start_times to show tiebreaker
mochi.add_task(Task(routine_name="Feeding",       frequency="daily",  duration=10, priority=Priority.HIGH,   start_time="08:30"))
mochi.add_task(Task(routine_name="Grooming",      frequency="weekly", duration=20, priority=Priority.LOW,    start_time="10:00"))

# Tasks for Biscuit — mix of priorities + times
biscuit.add_task(Task(routine_name="Morning walk", frequency="daily",  duration=30, priority=Priority.HIGH,   start_time="07:00"))
biscuit.add_task(Task(routine_name="Medication",   frequency="daily",  duration=5,  priority=Priority.HIGH,   start_time="08:00"))
biscuit.add_task(Task(routine_name="Play session", frequency="daily",  duration=25, priority=Priority.MEDIUM, start_time="09:00"))
biscuit.add_task(Task(routine_name="Bath",         frequency="weekly", duration=40, priority=Priority.LOW))

owner.add_pet(mochi)
owner.add_pet(biscuit)

# --- All tasks (unsorted) ---
print(f"\n PawPal+ -- {owner.get_name()}'s pets\n")

for pet in owner.get_pets():
    icon = SPECIES_ICON.get(pet.species, "🐾")
    rows = []
    for t in pet.get_tasks():
        p = Priority(t.get_priority())
        rows.append([
            PRIORITY_ICON[p],
            t.get_routine_name(),
            f"{t.get_duration()} min",
            PRIORITY_LABEL[p],
            t.start_time or "--",
            t.get_frequency(),
        ])
    print(f"{icon}  {pet.get_name()} ({pet.species})")
    print(tabulate(rows, headers=["", "Task", "Duration", "Priority", "Start", "Freq"], tablefmt="rounded_outline"))
    print()

# --- Schedule (priority-first, time tiebreaker) ---
scheduler = Scheduler(owner=owner, available_time=90)
plan = scheduler.generate()
skipped = [t for t in scheduler.get_all_tasks() if t not in plan]

print("=" * 54)
print("  Today's Schedule  (90 min available)")
print("=" * 54)

schedule_rows = []
for task in plan:
    p = Priority(task.get_priority())
    schedule_rows.append([
        PRIORITY_ICON[p],
        task.start_time or "--",
        task.get_routine_name(),
        f"{task.get_duration()} min",
        PRIORITY_LABEL[p],
    ])

print(tabulate(schedule_rows, headers=["", "Time", "Task", "Duration", "Priority"], tablefmt="rounded_outline"))

total = scheduler.get_total_duration(plan)
print(f"\n  Scheduled: {len(plan)} tasks -- {total} / 90 min used")

if skipped:
    print(f"\n  Skipped ({len(skipped)}):")
    for t in skipped:
        p = Priority(t.get_priority())
        print(f"     {PRIORITY_ICON[p]} {t.get_routine_name()} ({t.get_duration()} min, {PRIORITY_LABEL[p]}) -- didn't fit")

# --- Priority sort explanation ---
print("\n--- Sort order: HIGH priority tasks, sorted by start_time ---")
high_tasks = [t for t in plan if t.get_priority() == Priority.HIGH]
for i, t in enumerate(high_tasks, 1):
    print(f"  {i}. {t.get_routine_name():<18} [start_time={t.start_time}]  priority={t.get_priority()}")
