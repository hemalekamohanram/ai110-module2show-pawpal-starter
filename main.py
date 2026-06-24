from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="cat")
biscuit = Pet(name="Biscuit", species="dog")

# Tasks for Mochi
mochi.add_task(Task(routine_name="Feeding",       frequency="daily",  duration=10, priority=3))
mochi.add_task(Task(routine_name="Grooming",      frequency="weekly", duration=20, priority=1))

# Tasks for Biscuit
biscuit.add_task(Task(routine_name="Morning walk", frequency="daily",  duration=30, priority=3))
biscuit.add_task(Task(routine_name="Medication",   frequency="daily",  duration=5,  priority=3))
biscuit.add_task(Task(routine_name="Play session", frequency="daily",  duration=25, priority=2))
biscuit.add_task(Task(routine_name="Bath",         frequency="weekly", duration=40, priority=1))

owner.add_pet(mochi)
owner.add_pet(biscuit)

# --- Schedule ---
scheduler = Scheduler(owner=owner, available_time=90)
plan = scheduler.generate()

# --- Output ---
print(f"Today's Schedule for {owner.get_name()}'s pets")
print("=" * 42)

start_hour, start_min = 8, 0
for task in plan:
    time_str = f"{start_hour:02d}:{start_min:02d}"
    priority_label = {1: "low", 2: "medium", 3: "high"}.get(task.get_priority(), "?")
    print(f"  {time_str}  {task.get_routine_name():<18} {task.get_duration():>3} min  [{priority_label}]")
    start_min += task.get_duration()
    start_hour += start_min // 60
    start_min %= 60

total = scheduler.get_total_duration(plan)
print("=" * 42)
print(f"  Total scheduled: {total} / {scheduler.available_time} min")
print(f"  Tasks scheduled: {len(plan)} of {len(scheduler.get_all_tasks())} available")
