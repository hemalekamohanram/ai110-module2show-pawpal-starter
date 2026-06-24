import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# --- happy path ---

def test_mark_complete_changes_status():
    task = Task(routine_name="Morning walk", frequency="daily", duration=30, priority=3)
    assert task.is_completed() == False
    task.mark_complete()
    assert task.is_completed() == True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(routine_name="Feeding", frequency="daily", duration=10, priority=3))
    assert len(pet.get_tasks()) == 1


# --- edge cases ---

def test_generate_with_zero_available_time_returns_empty():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(routine_name="Feeding", frequency="daily", duration=10, priority=3))
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, available_time=0)
    assert scheduler.generate() == []


def test_generate_when_all_tasks_too_long_returns_empty():
    owner = Owner(name="Jordan")
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(routine_name="Long walk", frequency="daily", duration=120, priority=3))
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, available_time=30)
    assert scheduler.generate() == []


def test_get_total_duration_with_no_tasks_returns_zero():
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.get_total_duration() == 0


def test_get_all_tasks_with_no_pets_returns_empty():
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.get_all_tasks() == []


def test_remove_task_not_in_list_raises_error():
    pet = Pet(name="Mochi", species="cat")
    task = Task(routine_name="Feeding", frequency="daily", duration=10, priority=3)
    with pytest.raises(ValueError):
        pet.remove_task(task)
