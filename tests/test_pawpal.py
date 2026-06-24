from pawpal_system import Task, Pet


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
