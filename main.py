from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="cat")
biscuit = Pet(name="Biscuit", species="dog")

today = date.today()

# Tasks for Mochi — start_times added out of order intentionally
mochi.add_task(Task(routine_name="Feeding",  frequency="daily",  duration=10, priority=3, start_time="12:00", due_date=today))
mochi.add_task(Task(routine_name="Grooming", frequency="weekly", duration=20, priority=1, start_time="08:00", due_date=today))

# Tasks for Biscuit — also out of order; Medication marked complete
biscuit.add_task(Task(routine_name="Play session", frequency="daily",  duration=25, priority=2, start_time="15:30", due_date=today))
biscuit.add_task(Task(routine_name="Morning walk", frequency="daily",  duration=30, priority=3, start_time="07:00", due_date=today))
biscuit.add_task(Task(routine_name="Medication",   frequency="daily",  duration=5,  priority=3, start_time="09:00", due_date=today, completed=True))
biscuit.add_task(Task(routine_name="Bath",         frequency="weekly", duration=40, priority=1, start_time="11:00", due_date=today))

owner.add_pet(mochi)
owner.add_pet(biscuit)

scheduler = Scheduler(owner=owner, available_time=90)

# ── Demo 1: sort ALL tasks by start_time ──────────────────────────────────────
print("All tasks sorted by time")
print("=" * 42)
all_sorted = scheduler.sort_by_time(scheduler.get_all_tasks())
for t in all_sorted:
    status = "done" if t.is_completed() else "    "
    print(f"  {t.start_time}  [{status}]  {t.get_routine_name()}")

# ── Demo 2: filter — pending tasks only ──────────────────────────────────────
print()
print("Pending (not yet completed) tasks")
print("=" * 42)
pending = scheduler.filter_by_status(completed=False)
for t in pending:
    print(f"  {t.get_routine_name():<18} priority={t.get_priority()}")

# ── Demo 3: filter — completed tasks only ────────────────────────────────────
print()
print("Completed tasks")
print("=" * 42)
done = scheduler.filter_by_status(completed=True)
for t in done:
    print(f"  {t.get_routine_name()}")

# ── Demo 4: filter by pet name ───────────────────────────────────────────────
print()
print("Biscuit's tasks (filtered by pet)")
print("=" * 42)
biscuit_tasks = scheduler.filter_by_pet("Biscuit")
for t in scheduler.sort_by_time(biscuit_tasks):
    print(f"  {t.start_time}  {t.get_routine_name()}")

# ── Original schedule (priority-based greedy) ────────────────────────────────
print()
print(f"Today's Schedule for {owner.get_name()}'s pets")
print("=" * 42)
plan = scheduler.generate()
for task in plan:
    priority_label = {1: "low", 2: "medium", 3: "high"}.get(task.get_priority(), "?")
    print(f"  {task.start_time}  {task.get_routine_name():<18} {task.get_duration():>3} min  [{priority_label}]")

total = scheduler.get_total_duration(plan)
print("=" * 42)
print(f"  Total scheduled: {total} / {scheduler.available_time} min")
print(f"  Tasks scheduled: {len(plan)} of {len(scheduler.get_all_tasks())} available")

# ── Demo 5: conflict detection ───────────────────────────────────────────────
print()
print("Conflict detection demo")
print("=" * 42)

# Re-fetch pet references so we're working with the live objects in the owner.
mochi_pet   = next(p for p in owner.get_pets() if p.get_name() == "Mochi")
biscuit_pet = next(p for p in owner.get_pets() if p.get_name() == "Biscuit")

# Intentionally add two tasks at the same start_time to trigger conflicts:
#   "Vet check"  for Mochi    at 07:00  (same slot as Biscuit's Morning walk)
#   "Nail trim"  for Biscuit  at 07:00  (makes three tasks land on 07:00)
mochi_pet.add_task(Task(
    routine_name="Vet check", frequency="daily", duration=30,
    priority=3, start_time="07:00", due_date=today,
))
biscuit_pet.add_task(Task(
    routine_name="Nail trim", frequency="weekly", duration=15,
    priority=2, start_time="07:00", due_date=today,
))

print("Tasks at 07:00 (intentional conflict):")
print("  Morning walk (Biscuit), Vet check (Mochi), Nail trim (Biscuit)")
print()

warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(w)
else:
    print("  No conflicts found.")

# Show that a clean task list produces no warnings.
print()
print("No-conflict check (only 12:00 and 15:30 tasks):")
clean_tasks = [
    t for t in scheduler.get_all_tasks()
    if t.start_time in ("12:00", "15:30")
]
clean_warnings = scheduler.detect_conflicts(clean_tasks)
print(f"  Warnings returned: {len(clean_warnings)}  ✓ clean")

# ── Demo 6: mark_task_complete — recurring task auto-scheduling ───────────────
print()
print("Recurring task demo (timedelta auto-scheduling)")
print("=" * 42)

# Daily task: Feeding (Mochi)
feeding = next(t for t in mochi_pet.get_tasks() if t.get_routine_name() == "Feeding")
print(f"Mochi tasks before: {len(mochi_pet.get_tasks())}")
next_feeding = scheduler.mark_task_complete(feeding, mochi_pet)
print(f"Mochi tasks after completing 'Feeding' (daily): {len(mochi_pet.get_tasks())}")
print(f"  Original due: {feeding.due_date}  completed={feeding.is_completed()}")
print(f"  Next occurrence due: {next_feeding.due_date}  (today + 1 day via timedelta)")

print()

# Weekly task: Grooming (Mochi)
grooming = next(t for t in mochi_pet.get_tasks() if t.get_routine_name() == "Grooming")
print(f"Mochi tasks before: {len(mochi_pet.get_tasks())}")
next_grooming = scheduler.mark_task_complete(grooming, mochi_pet)
print(f"Mochi tasks after completing 'Grooming' (weekly): {len(mochi_pet.get_tasks())}")
print(f"  Original due: {grooming.due_date}  completed={grooming.is_completed()}")
print(f"  Next occurrence due: {next_grooming.due_date}  (today + 7 days via timedelta)")
