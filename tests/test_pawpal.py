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


def test_pet_sort_by_time_handles_unscheduled_tasks():
    pet = Pet(id="p4", name="Luna", species="cat", age=1)

    task_scheduled = Task(
        id="t30",
        description="Groom",
        duration_minutes=20,
        scheduled_start=datetime(2026, 4, 1, 10, 0),
        scheduled_end=datetime(2026, 4, 1, 10, 20),
    )
    task_unscheduled = Task(
        id="t31",
        description="Brush",
        duration_minutes=5,
        scheduled_start=None,
        scheduled_end=None,
    )

    pet.add_task(task_unscheduled)
    pet.add_task(task_scheduled)

    sorted_tasks = pet.sort_by_time()

    assert sorted_tasks[0].id == "t30"
    assert sorted_tasks[-1].id == "t31"


def test_task_mark_completed_daily_creates_next_task():
    task = Task(
        id="t40",
        description="Feed",
        duration_minutes=15,
        frequency="daily",
    )

    next_task = task.mark_completed(when=datetime(2026, 4, 1, 8, 0))

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.description == "Feed"
    assert "t40_next_20260402" in next_task.id
    assert next_task.is_completed is False


def test_scheduler_assign_times_with_limited_window():
    owner = Owner(id="o3", name="Sam")
    pet = Pet(id="p5", name="Otis", species="dog", age=5)
    owner.add_pet(pet)

    t1 = Task(id="t50", description="Play", duration_minutes=30)
    t2 = Task(id="t51", description="Walk", duration_minutes=60)
    t3 = Task(id="t52", description="Vet", duration_minutes=120)

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    scheduler = Scheduler()
    assigned = scheduler.assign_times(owner, datetime(2026, 4, 1, 9, 0), datetime(2026, 4, 1, 10, 30))

    assert len(assigned) == 2
    assert assigned[0].id == "t50"
    assert assigned[1].id == "t51"
    assert assigned[1].scheduled_end == datetime(2026, 4, 1, 10, 30)


def test_detect_conflicts_boundary_no_overlap():
    task_a = Task(
        id="t60",
        description="A",
        duration_minutes=30,
        scheduled_start=datetime(2026, 4, 1, 9, 0),
        scheduled_end=datetime(2026, 4, 1, 9, 30),
    )
    task_b = Task(
        id="t61",
        description="B",
        duration_minutes=30,
        scheduled_start=datetime(2026, 4, 1, 9, 30),
        scheduled_end=datetime(2026, 4, 1, 10, 0),
    )

    scheduler = Scheduler()
    warnings = scheduler.detect_conflicts([task_a, task_b])

    assert warnings == []


def test_get_tasks_filtered_invalid_status_raises():
    owner = Owner(id="o4", name="Taylor")
    pet = Pet(id="p6", name="Mochi", species="cat", age=3)
    owner.add_pet(pet)

    with pytest.raises(ValueError):
        owner.get_tasks_filtered(status="unknown")

