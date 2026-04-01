from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    id: str
    type: str
    duration_minutes: int
    priority: int  # 1=highest
    due_by: datetime
    is_completed: bool = False
    status: str = "pending"  # pending, scheduled, completed, missed

    def mark_completed(self):
        self.is_completed = True
        self.status = "completed"

    def mark_missed(self):
        self.status = "missed"

    def reschedule(self, new_due_by: datetime):
        self.due_by = new_due_by
        self.status = "pending"


@dataclass
class Availability:
    start: datetime
    end: datetime
    label: Optional[str] = None

    def overlaps(self, other: "Availability") -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment <= self.end


@dataclass
class Pet:
    id: str
    name: str
    age: int
    owner_id: str
    tasks: List[Task] = field(default_factory=list)

    def get_needs(self) -> List[Task]:
        return [t for t in self.tasks if not t.is_completed]

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]


@dataclass
class User:
    id: str
    name: str
    pets: List[Pet] = field(default_factory=list)
    availability: List[Availability] = field(default_factory=list)

    def get_free_slots(self, date: datetime) -> List[Availability]:
        return [a for a in self.availability if a.contains(date)]

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def add_availability(self, slot: Availability):
        self.availability.append(slot)


@dataclass
class ScheduledTask:
    task: Task
    start: datetime
    end: datetime
    reason: str
    score: float


class Scheduler:
    def schedule_tasks(self, user: User, tasks: List[Task]) -> List[ScheduledTask]:
        # skeleton: implement scheduling logic here
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        scheduled: List[ScheduledTask] = []

        for task in sorted_tasks:
            # TODO: fit into availability and create ScheduledTask
            pass

        return scheduled

    def resolve_conflicts(self, schedule: List[ScheduledTask]) -> List[ScheduledTask]:
        # skeleton: remove overlapping tasks
        return sorted(schedule, key=lambda item: item.start)

    def explain_plan(self, scheduled: List[ScheduledTask]) -> str:
        lines = [f"{s.task.type} at {s.start} because {s.reason}" for s in scheduled]
        return "\n".join(lines)
