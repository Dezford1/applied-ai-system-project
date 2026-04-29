from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ------------------------
# Task Class
# ------------------------
@dataclass
class Task:
    name: str
    type: str
    duration: int  # in minutes
    priority: int  # 1=high, 2=medium, 3=low
    time_window: Optional[Tuple[int, int]] = None
    completed: bool = False
    recurring: bool = False
    recurrence: Optional[str] = None
    recurrence_day: Optional[str] = None
    next_occurrence_day: Optional[str] = None

    def mark_complete(self):
        self.completed = True

    def is_conflict(self, other_task: "Task") -> bool:
        if not self.time_window or not other_task.time_window:
            return False
        start1, end1 = self.time_window
        start2, end2 = other_task.time_window
        return max(start1, start2) < min(end1, end2)


# ------------------------
# Pet Class
# ------------------------
@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        self.tasks = [t for t in self.tasks if t.name != task_name]


# ------------------------
# Owner Class
# ------------------------
@dataclass
class Owner:
    name: str
    email: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        self.pets = [p for p in self.pets if p.name != pet_name]


# ------------------------
# Scheduler Class
# ------------------------
class Scheduler:

    WEEK_DAYS = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    def get_all_tasks(self, owner: Owner) -> List[Tuple[Pet, Task]]:
        return [(pet, task) for pet in owner.pets for task in pet.tasks]

    def sort_by_time(self, tasks):
        def key(item):
            task = item[1]
            start = task.time_window[0] if task.time_window else 24 * 60
            return (start, task.priority, task.duration, task.name.lower())

        return sorted(tasks, key=key)

    def filter_tasks(self, tasks, pet_name=None, completed=None):
        filtered = tasks

        if pet_name:
            filtered = [t for t in filtered if t[0].name == pet_name]

        if completed is not None:
            filtered = [t for t in filtered if t[1].completed == completed]

        return filtered

    def detect_conflict_warnings(self, tasks):
        warnings = []
        ordered = self.sort_by_time(tasks)

        for i in range(len(ordered)):
            pet_a, task_a = ordered[i]
            for j in range(i + 1, len(ordered)):
                pet_b, task_b = ordered[j]

                if task_a.is_conflict(task_b):
                    scope = "same pet" if pet_a.name == pet_b.name else "different pets"
                    warnings.append(
                        f"WARNING: {scope} conflict between "
                        f"{pet_a.name}:{task_a.name} and {pet_b.name}:{task_b.name}"
                    )

        return warnings

    def build_budgeted_plan(self, tasks, budget):
        scheduled = []
        unscheduled = []
        used = 0

        for pet, task in self.sort_by_time(tasks):

            if used + task.duration > budget:
                unscheduled.append((pet, task, "over budget"))
                continue

            conflict = False
            for _, s_task in scheduled:
                if task.is_conflict(s_task):
                    unscheduled.append((pet, task, f"conflicts with {s_task.name}"))
                    conflict = True
                    break

            if conflict:
                continue

            scheduled.append((pet, task))
            used += task.duration

        return scheduled, unscheduled

    def explain_plan(self, plan):
        lines = []
        for pet, task in plan:
            start = (
                f"{task.time_window[0]//60:02d}:{task.time_window[0]%60:02d}"
                if task.time_window else "N/A"
            )
            end = (
                f"{task.time_window[1]//60:02d}:{task.time_window[1]%60:02d}"
                if task.time_window else "N/A"
            )

            lines.append(
                f"{pet.name}'s '{task.name}' scheduled {start}-{end}, "
                f"priority {task.priority}, duration {task.duration} min."
            )

        return "\n".join(lines)

    # ------------------------
    # 🤖 AGENTIC AI LAYER (FIXED + INSIDE CLASS)
    # ------------------------

    def evaluate_plan(self, scheduled, unscheduled, budget):
        issues = []

        total_time = sum(task.duration for _, task in scheduled)

        if total_time > budget:
            issues.append("Over budget")

        task_types = [task.type for _, task in scheduled]
        if "feeding" not in task_types:
            issues.append("Missing feeding task")

        return issues

    def build_agentic_plan(self, tasks, budget):

    # 🔍 RAG STEP: retrieve knowledge
        rules = self.retrieve_rules()

        scheduled, unscheduled = self.build_budgeted_plan(tasks, budget)

        issues = self.evaluate_plan(scheduled, unscheduled, budget)

    # 🧠 NEW: rule-based adjustment (this is your “RAG influence”)
        for rule in rules:
            if "Feeding tasks must be prioritized" in rule:
                scheduled.sort(key=lambda x: 0 if x[1].type == "feeding" else 1)

        attempts = 0
        while issues and attempts < 2:
            scheduled, unscheduled = self.build_budgeted_plan(tasks, budget)
            issues = self.evaluate_plan(scheduled, unscheduled, budget)
            attempts += 1

        return scheduled, unscheduled
    
    def retrieve_rules(self):
        from pet_knowledge import PET_CARE_RULES
        return PET_CARE_RULES
    
    def mark_task_complete(self, owner: Owner, pet_name: str, task_name: str, completed_day: str = None):
        """Mark a task complete for a pet and, if recurring, spawn the next instance.

        Returns the newly created next task if spawned, otherwise None.
        """
        # find pet
        pet = next((p for p in owner.pets if p.name == pet_name), None)
        if not pet:
            return None

        # find task (first matching name that is not already completed)
        task = next((t for t in pet.tasks if t.name == task_name and not t.completed), None)
        if not task:
            return None

        # mark complete
        task.mark_complete()

        # handle recurring
        if not task.recurring:
            return None

        # compute next occurrence day
        next_day = None
        if task.recurrence == "daily":
            if completed_day in self.WEEK_DAYS:
                idx = self.WEEK_DAYS.index(completed_day)
                next_day = self.WEEK_DAYS[(idx + 1) % len(self.WEEK_DAYS)]
            else:
                next_day = None
        elif task.recurrence == "weekly":
            next_day = task.recurrence_day or completed_day

        # spawn next task instance
        new_task = Task(
            name=task.name,
            type=task.type,
            duration=task.duration,
            priority=task.priority,
            time_window=task.time_window,
            recurring=task.recurring,
            recurrence=task.recurrence,
            recurrence_day=task.recurrence_day,
            next_occurrence_day=next_day,
        )

        pet.add_task(new_task)
        return new_task