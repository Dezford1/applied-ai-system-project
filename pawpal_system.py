# pawpal_system.py
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
    time_window: Optional[Tuple[int, int]] = None  # start/end in minutes from 0:00
    completed: bool = False
    recurring: bool = False
    recurrence: Optional[str] = None  # "daily" or "weekly"
    recurrence_day: Optional[str] = None  # day name if weekly
    next_occurrence_day: Optional[str] = None

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True

    def is_conflict(self, other_task: "Task") -> bool:
        """Check if this task conflicts with another task using time_window."""
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
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task by name."""
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
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]


# ------------------------
# Scheduler Class
# ------------------------
class Scheduler:
    """Scheduler handles sorting, filtering, conflict detection, and planning."""

    WEEK_DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def get_all_tasks(self, owner: Owner) -> List[Tuple[Pet, Task]]:
        """Return a flattened list of all (pet, task) tuples."""
        all_tasks = []
        for pet in owner.pets:
            for task in pet.tasks:
                all_tasks.append((pet, task))
        return all_tasks

    def sort_by_time(self, tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """
        Return tasks in execution order using deterministic time-first sorting.

        Sorting priority:
        1) earliest time_window start
        2) task priority (1 is highest)
        3) shorter duration
        4) task name for stable ordering

        Tasks without a time window are placed at the end.
        """
        def task_key(item):
            task = item[1]
            if task.time_window:
                start_minutes = task.time_window[0]
            else:
                start_minutes = 24 * 60  # tasks without a time_window go last
            return (start_minutes, task.priority, task.duration, task.name.lower())

        return sorted(tasks, key=task_key)

    def filter_tasks(
        self,
        tasks: List[Tuple[Pet, Task]],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Tuple[Pet, Task]]:
        """
        Filter a list of (pet, task) tuples by optional pet and completion status.

        Args:
            tasks: Candidate (pet, task) pairs.
            pet_name: Keep only tasks belonging to this pet when provided.
            completed: Keep only tasks with this completion flag when provided.

        Returns:
            Filtered list preserving original tuple shape.
        """
        filtered = tasks
        if pet_name:
            filtered = [item for item in filtered if item[0].name == pet_name]
        if completed is not None:
            filtered = [item for item in filtered if item[1].completed == completed]
        return filtered

    def detect_basic_conflicts(self, tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Task, Task]]:
        """
        Detect all overlapping time-window conflicts across the provided tasks.

        This performs pairwise overlap checks after time sorting and returns the
        conflicting task pairs.
        """
        conflicts: List[Tuple[Task, Task]] = []
        ordered = self.sort_by_time(tasks)
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                task_a = ordered[i][1]
                task_b = ordered[j][1]
                if task_a.is_conflict(task_b):
                    conflicts.append((task_a, task_b))
        return conflicts

    def detect_conflict_warnings(self, tasks: List[Tuple[Pet, Task]]) -> List[str]:
        """
        Lightweight conflict detection that returns warnings instead of exceptions.

        The scheduler continues planning even when conflicts are found. Each
        warning identifies whether the overlap is for the same pet or different
        pets so users can decide how to adjust tasks.

        Returns:
            List of human-readable warning messages.
        """
        warnings: List[str] = []
        ordered = self.sort_by_time(tasks)

        for i in range(len(ordered)):
            pet_a, task_a = ordered[i]
            for j in range(i + 1, len(ordered)):
                pet_b, task_b = ordered[j]

                if task_a.is_conflict(task_b):
                    scope = "same pet" if pet_a.name == pet_b.name else "different pets"
                    warnings.append(
                        f"WARNING: {scope} conflict between {pet_a.name}:{task_a.name} "
                        f"and {pet_b.name}:{task_b.name}."
                    )

        return warnings

    def is_task_due_today(self, task: Task, day_name: Optional[str] = None) -> bool:
        """
        Return True when a task is due on the provided day.

        Supports one-off tasks, daily recurring tasks, weekly recurring tasks,
        and next_occurrence_day overrides created after completion rollover.
        """
        if not task.recurring:
            return True
        recurrence = (task.recurrence or "daily").lower()
        today_name = day_name or "Monday"  # default for testing

        if task.next_occurrence_day:
            return task.next_occurrence_day.lower() == today_name.lower()

        if recurrence == "daily":
            return True
        if recurrence == "weekly":
            if not task.recurrence_day:
                return True
            return task.recurrence_day.lower() == today_name.lower()
        return True

    def _next_day_name(self, day_name: str) -> str:
        """Return the next weekday label, wrapping Sunday to Monday."""
        if day_name not in self.WEEK_DAYS:
            return "Monday"
        day_index = self.WEEK_DAYS.index(day_name)
        return self.WEEK_DAYS[(day_index + 1) % len(self.WEEK_DAYS)]

    def _next_occurrence_day(self, task: Task, completed_day: str) -> str:
        """
        Compute the next due day label after marking a recurring task complete.

        Daily tasks move to the next day. Weekly tasks keep their recurrence day.
        """
        recurrence = (task.recurrence or "daily").lower()

        if recurrence == "daily":
            return self._next_day_name(completed_day)

        if recurrence == "weekly":
            if task.recurrence_day:
                return task.recurrence_day
            return completed_day

        return completed_day

    def _spawn_next_recurring_task(self, task: Task, completed_day: str) -> Task:
        """
        Create a fresh incomplete task instance for the next recurrence cycle.

        The new instance preserves task metadata and sets next_occurrence_day.
        """
        return Task(
            name=task.name,
            type=task.type,
            duration=task.duration,
            priority=task.priority,
            time_window=task.time_window,
            completed=False,
            recurring=task.recurring,
            recurrence=task.recurrence,
            recurrence_day=task.recurrence_day,
            next_occurrence_day=self._next_occurrence_day(task, completed_day),
        )

    def mark_task_complete(
        self,
        owner: Owner,
        pet_name: str,
        task_name: str,
        completed_day: str = "Monday",
    ) -> Optional[Task]:
        """
        Mark a task complete and auto-create the next instance for recurring tasks.

        Args:
            owner: Owner containing the target pet/task.
            pet_name: Pet whose task should be completed.
            task_name: Task to mark complete.
            completed_day: Day label used to calculate the next occurrence.

        Returns:
            The newly created recurring task instance, or None.
        """
        for pet in owner.pets:
            if pet.name != pet_name:
                continue

            for task in pet.tasks:
                if task.name == task_name and not task.completed:
                    task.mark_complete()

                    recurrence = (task.recurrence or "").lower()
                    if task.recurring and recurrence in {"daily", "weekly"}:
                        next_task = self._spawn_next_recurring_task(task, completed_day)
                        pet.add_task(next_task)
                        return next_task

                    return None

        return None

    def build_budgeted_plan(
        self, tasks: List[Tuple[Pet, Task]], daily_budget_minutes: int
    ) -> Tuple[List[Tuple[Pet, Task]], List[Tuple[Pet, Task, str]]]:
        """
        Build a daily plan that respects a minute budget and conflict constraints.

        Greedy strategy:
        1) sort by time
        2) schedule while budget remains
        3) skip conflicting tasks

        Returns:
            A tuple of (scheduled_tasks, unscheduled_tasks_with_reason).
        """
        scheduled: List[Tuple[Pet, Task]] = []
        unscheduled: List[Tuple[Pet, Task, str]] = []
        used_minutes = 0

        for pet, task in self.sort_by_time(tasks):
            if used_minutes + task.duration > daily_budget_minutes:
                unscheduled.append((pet, task, "over daily time budget"))
                continue

            conflict_with = None
            for _, scheduled_task in scheduled:
                if task.is_conflict(scheduled_task):
                    conflict_with = scheduled_task.name
                    break

            if conflict_with:
                unscheduled.append((pet, task, f"conflicts with {conflict_with}"))
                continue

            scheduled.append((pet, task))
            used_minutes += task.duration

        return scheduled, unscheduled

    def explain_plan(self, plan: List[Tuple[Pet, Task]]) -> str:
        """Return a simple explanation string for the scheduled plan."""
        explanation = []
        for pet, task in plan:
            start = f"{task.time_window[0]//60:02d}:{task.time_window[0]%60:02d}" if task.time_window else "N/A"
            end = f"{task.time_window[1]//60:02d}:{task.time_window[1]%60:02d}" if task.time_window else "N/A"
            explanation.append(
                f"{pet.name}'s task '{task.name}' is scheduled {start}-{end}, "
                f"priority {task.priority}, duration {task.duration} min."
            )
        return "\n".join(explanation)