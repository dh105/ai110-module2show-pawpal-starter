from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime

# Example usage
if __name__ == "__main__":
    owner = Owner(id="o1", name="Alex")

    # Pets
    pet1 = Pet(id="p1", name="Rufus", species="dog", age=3)
    pet2 = Pet(id="p2", name="Luna", species="cat", age=1)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Tasks (out of order add + mixed completion)
    task1 = Task(id="t1", description="Walk Rufus", duration_minutes=30, frequency="daily")
    task2 = Task(id="t2", description="Feed Rufus", duration_minutes=15, frequency="daily")
    task3 = Task(id="t3", description="Groom Luna", duration_minutes=45, frequency="weekly")
    task4 = Task(id="t4", description="Vet appointment", duration_minutes=60, frequency="weekly")

    # mark one completed for filtering tests
    task2.mark_completed()

    pet1.add_task(task4)
    pet2.add_task(task3)
    pet1.add_task(task2)
    pet1.add_task(task1)

    scheduler = Scheduler()
    start_time = datetime(2026, 4, 1, 8, 0)
    end_time = datetime(2026, 4, 1, 12, 0)

    scheduled_tasks = scheduler.assign_times(owner, start_time, end_time)

    print("Today's Schedule")
    print("===============")
    print(scheduler.explain(scheduled_tasks))

    # Validate new filtering method on Owner
    print("\nAll tasks:")
    all_tasks = owner.get_tasks_filtered(status="all")
    for t in all_tasks:
        print(f"- {t.description} (completed={t.is_completed})")

    print("\nPending tasks:")
    pending = owner.get_tasks_filtered(status="pending")
    for t in pending:
        print(f"- {t.description}")

    print("\nCompleted tasks for Rufus:")
    completed_rufus = owner.get_tasks_filtered(status="completed", pet_name="Rufus")
    for t in completed_rufus:
        print(f"- {t.description}")

    # Demonstrate conflict detection with overlapping tasks
    print("\nConflict detection test:")
    overlapping_task1 = Task(
        id="t_overlap1",
        description="Overlap 1",
        duration_minutes=60,
        frequency="daily",
    )
    overlapping_task2 = Task(
        id="t_overlap2",
        description="Overlap 2",
        duration_minutes=30,
        frequency="daily",
    )

    overlapping_task1.scheduled_start = datetime(2026, 4, 1, 14, 0)
    overlapping_task1.scheduled_end = datetime(2026, 4, 1, 15, 0)
    overlapping_task2.scheduled_start = datetime(2026, 4, 1, 14, 30)
    overlapping_task2.scheduled_end = datetime(2026, 4, 1, 15, 0)

    conflict_warnings = scheduler.detect_conflicts([overlapping_task1, overlapping_task2])
    for warning in conflict_warnings:
        print(warning)


