import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(name="Walk", frequency="daily", duration=20, priority=2,
              completed=False, start_time=None, due_date=None):
    return Task(routine_name=name, frequency=frequency, duration=duration,
                priority=priority, completed=completed,
                start_time=start_time, due_date=due_date)


def make_scheduler(pets=None, available_time=90):
    owner = Owner(name="Jordan")
    for pet in (pets or []):
        owner.add_pet(pet)
    return Scheduler(owner=owner, available_time=available_time)


# ---------------------------------------------------------------------------
# Task — mark_complete
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.is_completed() is False
    task.mark_complete()
    assert task.is_completed() is True


def test_mark_complete_is_idempotent():
    task = make_task()
    task.mark_complete()
    task.mark_complete()  # calling twice should not raise
    assert task.is_completed() is True


# ---------------------------------------------------------------------------
# Task — next_occurrence
# ---------------------------------------------------------------------------

def test_next_occurrence_daily_advances_one_day():
    today = date.today()
    task = make_task(frequency="daily", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.due_date == today + timedelta(days=1)
    assert nxt.completed is False


def test_next_occurrence_weekly_advances_seven_days():
    today = date.today()
    task = make_task(frequency="weekly", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.due_date == today + timedelta(days=7)


def test_next_occurrence_uses_today_when_no_due_date():
    task = make_task(frequency="daily", due_date=None)
    nxt = task.next_occurrence()
    assert nxt.due_date == date.today() + timedelta(days=1)


def test_next_occurrence_unknown_frequency_returns_none():
    task = make_task(frequency="monthly", due_date=date.today())
    assert task.next_occurrence() is None


def test_next_occurrence_does_not_mutate_original():
    today = date.today()
    task = make_task(frequency="daily", due_date=today)
    task.next_occurrence()
    assert task.due_date == today      # original unchanged
    assert task.completed is False


# ---------------------------------------------------------------------------
# Pet — add / remove tasks
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_remove_task_decreases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    task = make_task()
    pet.add_task(task)
    pet.remove_task(task)
    assert len(pet.get_tasks()) == 0


def test_remove_task_not_in_list_raises_error():
    pet = Pet(name="Mochi", species="cat")
    task = make_task()
    with pytest.raises(ValueError):
        pet.remove_task(task)


# ---------------------------------------------------------------------------
# Scheduler — generate
# ---------------------------------------------------------------------------

def test_generate_with_zero_available_time_returns_empty():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task(duration=10, priority=3))
    s = make_scheduler(pets=[pet], available_time=0)
    assert s.generate() == []


def test_generate_when_all_tasks_too_long_returns_empty():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(make_task(duration=120, priority=3))
    s = make_scheduler(pets=[pet], available_time=30)
    assert s.generate() == []


def test_generate_schedules_high_priority_first():
    pet = Pet(name="Biscuit", species="dog")
    low = make_task(name="Bath",   duration=20, priority=1)
    high = make_task(name="Meds",  duration=10, priority=3)
    pet.add_task(low)
    pet.add_task(high)
    s = make_scheduler(pets=[pet], available_time=90)
    plan = s.generate()
    assert plan[0].get_routine_name() == "Meds"


def test_generate_skips_tasks_that_do_not_fit():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(make_task(name="Walk",  duration=50, priority=3))
    pet.add_task(make_task(name="Bath",  duration=50, priority=3))
    s = make_scheduler(pets=[pet], available_time=60)
    plan = s.generate()
    assert len(plan) == 1


def test_get_total_duration_with_no_tasks_returns_zero():
    s = make_scheduler(pets=[], available_time=60)
    assert s.get_total_duration() == 0


# ---------------------------------------------------------------------------
# Scheduler — sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_chronologically():
    pet = Pet(name="Mochi", species="cat")
    s = make_scheduler(pets=[pet])
    tasks = [
        make_task(name="C", start_time="10:00"),
        make_task(name="A", start_time="08:00"),
        make_task(name="B", start_time="09:00"),
    ]
    result = s.sort_by_time(tasks)
    assert [t.get_routine_name() for t in result] == ["A", "B", "C"]


def test_sort_by_time_tasks_without_start_time_go_last():
    pet = Pet(name="Mochi", species="cat")
    s = make_scheduler(pets=[pet])
    tasks = [
        make_task(name="No time"),
        make_task(name="Early", start_time="07:00"),
    ]
    result = s.sort_by_time(tasks)
    assert result[0].get_routine_name() == "Early"
    assert result[-1].get_routine_name() == "No time"


def test_sort_by_time_empty_list_returns_empty():
    s = make_scheduler()
    assert s.sort_by_time([]) == []


def test_sort_by_time_all_no_start_time_preserves_relative_order():
    pet = Pet(name="Mochi", species="cat")
    s = make_scheduler(pets=[pet])
    tasks = [make_task(name="X"), make_task(name="Y"), make_task(name="Z")]
    result = s.sort_by_time(tasks)
    assert len(result) == 3  # all end up at the back, no crash


# ---------------------------------------------------------------------------
# Scheduler — filter_by_status
# ---------------------------------------------------------------------------

def test_filter_by_status_returns_only_pending():
    pet = Pet(name="Mochi", species="cat")
    done = make_task(name="Done", completed=True)
    pending = make_task(name="Pending")
    pet.add_task(done)
    pet.add_task(pending)
    s = make_scheduler(pets=[pet])
    result = s.filter_by_status(completed=False)
    assert len(result) == 1
    assert result[0].get_routine_name() == "Pending"


def test_filter_by_status_returns_only_completed():
    pet = Pet(name="Mochi", species="cat")
    done = make_task(name="Done", completed=True)
    pending = make_task(name="Pending")
    pet.add_task(done)
    pet.add_task(pending)
    s = make_scheduler(pets=[pet])
    result = s.filter_by_status(completed=True)
    assert len(result) == 1
    assert result[0].get_routine_name() == "Done"


def test_filter_by_status_no_matches_returns_empty():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task())
    s = make_scheduler(pets=[pet])
    assert s.filter_by_status(completed=True) == []


# ---------------------------------------------------------------------------
# Scheduler — filter_by_pet
# ---------------------------------------------------------------------------

def test_filter_by_pet_returns_correct_tasks():
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    mochi.add_task(make_task(name="Feeding"))
    biscuit.add_task(make_task(name="Walk"))
    s = make_scheduler(pets=[mochi, biscuit])
    result = s.filter_by_pet("Mochi")
    assert len(result) == 1
    assert result[0].get_routine_name() == "Feeding"


def test_filter_by_pet_unknown_name_returns_empty():
    pet = Pet(name="Mochi", species="cat")
    s = make_scheduler(pets=[pet])
    assert s.filter_by_pet("Ghost") == []


def test_filter_by_pet_is_case_sensitive():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task())
    s = make_scheduler(pets=[pet])
    assert s.filter_by_pet("mochi") == []  # lowercase doesn't match


def test_filter_by_pet_no_pets_returns_empty():
    s = make_scheduler(pets=[])
    assert s.filter_by_pet("Anyone") == []


# ---------------------------------------------------------------------------
# Scheduler — detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_start_time():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task(name="Feeding",  start_time="08:00"))
    pet.add_task(make_task(name="Grooming", start_time="08:00"))
    s = make_scheduler(pets=[pet])
    warnings = s.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_no_conflicts_returns_empty():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task(name="Feeding",  start_time="08:00"))
    pet.add_task(make_task(name="Walk",     start_time="09:00"))
    s = make_scheduler(pets=[pet])
    assert s.detect_conflicts() == []


def test_detect_conflicts_ignores_tasks_with_no_start_time():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(make_task(name="A"))  # no start_time
    pet.add_task(make_task(name="B"))  # no start_time
    s = make_scheduler(pets=[pet])
    assert s.detect_conflicts() == []


def test_detect_conflicts_no_tasks_returns_empty():
    s = make_scheduler(pets=[])
    assert s.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Scheduler — mark_task_complete
# ---------------------------------------------------------------------------

def test_mark_task_complete_marks_task_done():
    pet = Pet(name="Mochi", species="cat")
    task = make_task(frequency="daily", due_date=date.today())
    pet.add_task(task)
    s = make_scheduler(pets=[pet])
    s.mark_task_complete(task, pet)
    assert task.is_completed() is True


def test_mark_task_complete_adds_next_occurrence_to_pet():
    pet = Pet(name="Mochi", species="cat")
    task = make_task(frequency="daily", due_date=date.today())
    pet.add_task(task)
    s = make_scheduler(pets=[pet])
    s.mark_task_complete(task, pet)
    assert len(pet.get_tasks()) == 2  # original + next occurrence


def test_mark_task_complete_next_due_date_is_tomorrow():
    today = date.today()
    pet = Pet(name="Mochi", species="cat")
    task = make_task(frequency="daily", due_date=today)
    pet.add_task(task)
    s = make_scheduler(pets=[pet])
    next_task = s.mark_task_complete(task, pet)
    assert next_task.due_date == today + timedelta(days=1)


def test_mark_task_complete_unknown_frequency_returns_none():
    pet = Pet(name="Mochi", species="cat")
    task = make_task(frequency="monthly", due_date=date.today())
    pet.add_task(task)
    s = make_scheduler(pets=[pet])
    result = s.mark_task_complete(task, pet)
    assert result is None
    assert len(pet.get_tasks()) == 1  # no new task added
