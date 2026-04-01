from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class Task:
    id: str
    description: str
    duration_minutes: int
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    frequency: Optional[str] = None  # e.g., "daily", "weekly"
    is_completed: bool = False

    def mark_completed(self, when: Optional[datetime] = None):
        """Mark this task as completed and create next recurring instance if needed."""
        self.is_completed = True
        if when is None:
            when = datetime.now()

        if self.frequency not in {"daily", "weekly"}:
            return None

        increment = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_start = when + increment

        # build next task id with ordinal date suffix to avoid collisions
        next_task_id = f"{self.id}_next_{next_start.strftime('%Y%m%d')}-{next_start.strftime('%H%M%S')}"

        return Task(
            id=next_task_id,
            description=self.description,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
        )

    def mark_pending(self):
        """Mark this task as not completed."""
        self.is_completed = False

    def has_schedule(self) -> bool:
        """Return True if the task has a scheduled interval assigned."""
        return self.scheduled_start is not None and self.scheduled_end is not None


@dataclass
class Pet:
    id: str
    name: str
    species: Optional[str] = None
    age: Optional[int] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a new task to the pet."""
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError("Task id already exists for this pet")
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        """Remove a task by id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return the task list for the pet."""
        return list(self.tasks)
    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted by scheduled time."""
        return sorted(self.tasks, key=lambda t: (t.scheduled_start or datetime.max))


@dataclass
class Owner:
    id: str
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to the owner."""
        if any(existing.id == pet.id for existing in self.pets):
            raise ValueError("Pet id already exists for this owner")
        self.pets.append(pet)

    def remove_pet(self, pet_id: str):
        """Remove a pet by id."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_all_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_pending_tasks(self) -> List[Task]:
        """Return all uncompleted tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.is_completed]

    def get_tasks_filtered(
        self,
        status: str = "all",
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by completion status and optional pet name."""
        valid_status = {"all", "pending", "completed"}
        if status not in valid_status:
            raise ValueError(f"Invalid status '{status}', must be one of {valid_status}")

        filtered = []
        for pet in self.pets:
            if pet_name and pet.name.lower() != pet_name.lower():
                continue

            for task in pet.tasks:
                if status == "all":
                    filtered.append(task)
                elif status == "pending" and not task.is_completed:
                    filtered.append(task)
                elif status == "completed" and task.is_completed:
                    filtered.append(task)

        return filtered


class Scheduler:
    def __init__(self):
        """Initialize the scheduler with an empty schedule."""
        self.schedule: List[Task] = []
        self.conflict_warnings: List[str] = []

    def retrieve_tasks(self, owner: Owner) -> List[Task]:
        """Retrieve pending tasks from the owner."""
        return owner.get_pending_tasks()

    def assign_times(self, owner: Owner, start_time: datetime, end_time: datetime) -> List[Task]:
        """Assign tasks to time slots between start_time and end_time."""
        remaining_minutes = int((end_time - start_time).total_seconds() / 60)
        pending = sorted(self.retrieve_tasks(owner), key=lambda t: (t.is_completed, t.duration_minutes, t.description))
        scheduled = []
        cursor = start_time

        for task in pending:
            if task.duration_minutes <= remaining_minutes:
                task.scheduled_start = cursor
                task.scheduled_end = cursor + timedelta(minutes=task.duration_minutes)
                remaining_minutes -= task.duration_minutes
                cursor = task.scheduled_end
                scheduled.append(task)
            else:
                continue

        self.schedule = scheduled
        self.conflict_warnings = self.detect_conflicts(scheduled)
        return scheduled

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return lightweight conflict warnings for overlapping scheduled tasks."""
        warnings = []
        sorted_tasks = sorted(tasks, key=lambda t: t.scheduled_start or datetime.max)

        for i in range(len(sorted_tasks)):
            a = sorted_tasks[i]
            if not a.has_schedule():
                continue
            for b in sorted_tasks[i + 1 :]:
                if not b.has_schedule():
                    continue
                # As tasks are ordered by start, any b that starts after a ends is no longer in conflict
                if b.scheduled_start >= a.scheduled_end:
                    break
                if a.scheduled_start < b.scheduled_end and b.scheduled_start < a.scheduled_end:
                    warnings.append(
                        f"Conflict: '{a.description}' ({a.scheduled_start.strftime('%H:%M')}-{a.scheduled_end.strftime('%H:%M')}) "
                        f"overlaps with '{b.description}' ({b.scheduled_start.strftime('%H:%M')}-{b.scheduled_end.strftime('%H:%M')})."
                    )

        return warnings

    def complete_task(self, owner: Owner, task_id: str, when: Optional[datetime] = None) -> Optional[Task]:
        """Mark a task completed and add next occurrence for daily/weekly tasks."""
        for pet in owner.pets:
            for task in pet.tasks:
                if task.id == task_id:
                    next_task = task.mark_completed(when=when)
                    if next_task is not None:
                        pet.add_task(next_task)
                    return next_task
        return None

    def get_today_schedule(self) -> List[Task]:
        """Return the current scheduled tasks for today."""
        return list(self.schedule)

    def explain(self, scheduled_tasks: Optional[List[Task]] = None) -> str:
        """Return a user-readable summary of scheduled tasks."""
        if scheduled_tasks is None:
            scheduled_tasks = self.get_today_schedule()
        if not scheduled_tasks:
            return "No tasks scheduled."

        lines = [
            f"{task.description} (Pet task) {task.scheduled_start.strftime('%H:%M')} - {task.scheduled_end.strftime('%H:%M')}"
            for task in scheduled_tasks
        ]

        if self.conflict_warnings:
            lines.append("\nWarnings:")
            lines.extend([f"- {w}" for w in self.conflict_warnings])

        return "\n".join(lines)


__all__ = ["Task", "Pet", "Owner", "Scheduler"]
