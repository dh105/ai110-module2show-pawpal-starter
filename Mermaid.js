// PawPal+ implementation of classes in JavaScript (pure JS, no Mermaid syntax)

class Pet {
  constructor({ id, name, age, owner }) {
    this.id = id;
    this.name = name;
    this.age = age;
    this.owner = owner;
    this.tasks = [];
  }

  getNeeds() {
    return this.tasks.filter(task => !task.isCompleted);
  }

  addTask(task) {
    this.tasks.push(task);
  }

  removeTask(taskId) {
    this.tasks = this.tasks.filter(t => t.id !== taskId);
  }
}

class User {
  constructor({ id, name }) {
    this.id = id;
    this.name = name;
    this.pets = [];
    this.availability = [];
  }

  getFreeSlots(date) {
    return this.availability.filter(slot => slot.isAvailableOn(date));
  }

  addPet(pet) {
    this.pets.push(pet);
  }

  addAvailability(slot) {
    this.availability.push(slot);
  }
}

class Task {
  constructor({ id, type, durationMinutes, priority, dueBy }) {
    this.id = id;
    this.type = type;
    this.durationMinutes = durationMinutes;
    this.priority = priority;
    this.dueBy = new Date(dueBy);
    this.isCompleted = false;
    this.status = 'pending'; // pending, scheduled, completed, missed
  }

  markCompleted() {
    this.isCompleted = true;
    this.status = 'completed';
  }

  markMissed() {
    this.status = 'missed';
  }

  reschedule(newDeadline) {
    this.dueBy = new Date(newDeadline);
    this.status = 'pending';
  }
}

class Availability {
  constructor({ start, end, label }) {
    this.start = new Date(start);
    this.end = new Date(end);
    this.label = label;
  }

  overlaps(other) {
    return this.start < other.end && other.start < this.end;
  }

  isAvailableOn(date) {
    const d = new Date(date);
    return this.start <= d && d <= this.end;
  }
}

class ScheduledTask {
  constructor({ task, start, end, reason, score }) {
    this.task = task;
    this.start = new Date(start);
    this.end = new Date(end);
    this.reason = reason;
    this.score = score;
  }
}

class Scheduler {
  scheduleTasks(user, tasks) {
    const sorted = [...tasks].sort((a, b) => a.priority - b.priority);
    const scheduled = [];

    for (const task of sorted) {
      const slot = user.availability.find(av => {
        const slotLength = (av.end - av.start) / (1000 * 60);
        return slotLength >= task.durationMinutes;
      });

      if (!slot) continue;

      const start = slot.start;
      const end = new Date(start.getTime() + task.durationMinutes * 60 * 1000);
      const reason = `Scheduled by priority ${task.priority}`;
      scheduled.push(new ScheduledTask({ task, start, end, reason, score: 1 }));
      task.status = 'scheduled';
      slot.start = end; // reduce the availability slot
    }

    return scheduled;
  }

  resolveConflicts(scheduledTasks) {
    return scheduledTasks.sort((a, b) => a.start - b.start);
  }

  explainPlan(scheduledTasks) {
    return scheduledTasks.map(st => `${st.task.type} at ${st.start.toISOString()} because ${st.reason}`).join('\n');
  }
}

module.exports = {
  Pet,
  User,
  Task,
  Availability,
  ScheduledTask,
  Scheduler,
};
