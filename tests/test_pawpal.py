import pytest
from datetime import datetime
from pawpal_system import Task, Pet


def test_task_completion_marks_task_done():
    task = Task(
        id="t1",
        description="Feed meal",
        duration_minutes=15,
        scheduled_start=None,
        scheduled_end=None,
        frequency="daily",
    )

    assert task.is_completed is False
    task.mark_completed()
    assert task.is_completed is True


def test_pet_add_task_increases_task_count():
    pet = Pet(id="p1", name="Rufus", species="dog", age=3)
    assert len(pet.tasks) == 0

    task = Task(
        id="t2",
        description="Walk",
        duration_minutes=30,
        scheduled_start=None,
        scheduled_end=None,
        frequency="daily",
    )

    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == "t2"
