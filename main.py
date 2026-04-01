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

    # Tasks
    task1 = Task(id="t1", description="Walk Rufus", duration_minutes=30, frequency="daily")
    task2 = Task(id="t2", description="Feed Rufus", duration_minutes=15, frequency="daily")
    task3 = Task(id="t3", description="Groom Luna", duration_minutes=45, frequency="weekly")

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)

    scheduler = Scheduler()
    start_time = datetime(2026, 4, 1, 8, 0)
    end_time = datetime(2026, 4, 1, 12, 0)

    scheduled_tasks = scheduler.assign_times(owner, start_time, end_time)

    print("Today's Schedule")
    print("===============")
    print(scheduler.explain(scheduled_tasks))


