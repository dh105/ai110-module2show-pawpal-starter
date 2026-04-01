import pytest
from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler


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


def test_complete_recurring_task_creates_next_occurrence():
    owner = Owner(id="o1", name="Alex")
    pet = Pet(id="p2", name="Milo", species="cat", age=2)
    owner.add_pet(pet)

    task = Task(
        id="t10",
        description="Feed Milo",
        duration_minutes=10,
        frequency="daily",
    )

    pet.add_task(task)
    scheduler = Scheduler()

    next_task = scheduler.complete_task(owner, task_id="t10", when=datetime(2026, 4, 1, 8, 0))

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.description == "Feed Milo"
    assert next_task.frequency == "daily"

    # new task should be in the pet tasks list and not marked completed
    assert any(t for t in pet.tasks if t.id == next_task.id)
    assert not next_task.is_completed


def test_scheduler_conflict_detection_lightweight():
    owner = Owner(id="o2", name="Dana")
    pet = Pet(id="p3", name="Bella", species="dog", age=4)
    owner.add_pet(pet)

    task_a = Task(id="t20", description="Morning walk", duration_minutes=60)
    task_b = Task(id="t21", description="Vet check", duration_minutes=30)

    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler()
    # intentionally force overlap by assigning start times manually
    task_a.scheduled_start = datetime(2026, 4, 1, 9, 0)
    task_a.scheduled_end = datetime(2026, 4, 1, 10, 0)
    task_b.scheduled_start = datetime(2026, 4, 1, 9, 30)
    task_b.scheduled_end = datetime(2026, 4, 1, 10, 0)

    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert len(warnings) == 1
    assert "overlaps with" in warnings[0]
