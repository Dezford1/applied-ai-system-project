from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pawpal_system import Owner, Pet, Task, Scheduler


def sort_tasks_by_time(tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
    """
    Sort tasks by earliest start time.
    Tasks without a time window are placed last.
    """
    return sorted(
        tasks,
        key=lambda x: (
            x[1].time_window[0] if x[1].time_window else 24 * 60,
            x[1].priority,
            x[1].duration,
            x[1].name.lower(),
        ),
    )


def filter_tasks(
    tasks: List[Tuple[Pet, Task]],
    pet_name: Optional[str] = None,
    completed: Optional[bool] = None,
) -> List[Tuple[Pet, Task]]:
    """Filter tasks by pet and/or completion status."""
    filtered = tasks

    if pet_name is not None:
        filtered = [item for item in filtered if item[0].name == pet_name]

    if completed is not None:
        filtered = [item for item in filtered if item[1].completed == completed]

    return filtered


def is_task_due_today(
    task: Task,
    recurrence_rules: Dict[str, Tuple[str, Optional[str]]],
    day_name: Optional[str] = None,
) -> bool:
    """Return True if task should be scheduled on the given day."""
    if task.name not in recurrence_rules:
        return True

    recurrence, recurrence_day = recurrence_rules[task.name]
    recurrence = recurrence.lower()
    today_name = day_name or datetime.now().strftime("%A")

    if recurrence == "daily":
        return True

    if recurrence == "weekly":
        if not recurrence_day:
            return True
        return recurrence_day.lower() == today_name.lower()

    return True


def detect_basic_conflicts(tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Task, Task]]:
    """Detect overlapping tasks using task time windows."""
    conflicts: List[Tuple[Task, Task]] = []
    ordered = sort_tasks_by_time(tasks)

    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            task_a = ordered[i][1]
            task_b = ordered[j][1]
            if task_a.is_conflict(task_b):
                conflicts.append((task_a, task_b))

    return conflicts


def build_budgeted_plan(
    tasks: List[Tuple[Pet, Task]], daily_budget_minutes: int
) -> Tuple[List[Tuple[Pet, Task]], List[Tuple[Pet, Task, str]]]:
    """
    Build a plan that respects daily budget and basic time-window conflicts.
    Returns scheduled tasks and unscheduled tasks with reasons.
    """
    scheduled: List[Tuple[Pet, Task]] = []
    unscheduled: List[Tuple[Pet, Task, str]] = []
    used_minutes = 0

    for pet, task in sort_tasks_by_time(tasks):
        if used_minutes + task.duration > daily_budget_minutes:
            unscheduled.append((pet, task, "over daily time budget"))
            continue

        conflict_with = None
        if task.time_window is not None:
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


# ------------------------
# Step 1: Create Owner
# ------------------------
owner = Owner("Dezmond", "dezmond@example.com")

# ------------------------
# Step 2: Create Pets
# ------------------------
dog = Pet("Buddy", "Dog", 3)
cat = Pet("Milo", "Cat", 2)

# ------------------------
# Step 3: Add Tasks
# ------------------------
# Dog Tasks
task1 = Task("Morning Walk", "walk", 30, 1, (480, 510), completed=True)
task2 = Task("Feed Dog", "feeding", 10, 2, (510, 520))

# Cat Tasks
task3 = Task("Feed Cat", "feeding", 10, 1, (500, 510))
task4 = Task("Brush Cat", "grooming", 15, 3, (510, 520))

dog.add_task(task1)
dog.add_task(task2)
cat.add_task(task3)
cat.add_task(task4)

owner.add_pet(dog)
owner.add_pet(cat)

# ------------------------
# Step 4: Gather and process tasks
# ------------------------
scheduler = Scheduler()
all_tasks = scheduler.get_all_tasks(owner)

# Recurring task rules keyed by task name: (recurrence, day_name_if_weekly)
recurrence_rules: Dict[str, Tuple[str, Optional[str]]] = {
    "Feed Dog": ("daily", None),
    "Feed Cat": ("weekly", "Monday"),
}

# Filter by completion status and due recurrence
today_name = datetime.now().strftime("%A")
incomplete_tasks = filter_tasks(all_tasks, completed=False)
due_today_tasks = [
    item
    for item in incomplete_tasks
    if is_task_due_today(item[1], recurrence_rules, today_name)
]

# Optional pet filter example
buddy_incomplete_tasks = filter_tasks(due_today_tasks, pet_name="Buddy", completed=False)

# Detect conflicts before scheduling using Scheduler warnings
warnings = scheduler.detect_conflict_warnings(due_today_tasks)

# Build final budgeted plan
DAILY_BUDGET_MINUTES = 45
today_plan, unscheduled_tasks = build_budgeted_plan(due_today_tasks, DAILY_BUDGET_MINUTES)

# ------------------------
# Step 5: Print output
# ------------------------
print("=== Today's Pet Care Schedule ===")
print(f"Today: {today_name}")
print(f"Incomplete tasks across pets: {len(incomplete_tasks)}")
print(f"Incomplete tasks for Buddy: {len(buddy_incomplete_tasks)}")

if warnings:
    print("\nConflict Warnings:")
    for warning in warnings:
        print(f"- {warning}")

print("\nScheduled Tasks:")
for pet, task in today_plan:
    start_time = (
        f"{task.time_window[0]//60:02d}:{task.time_window[0] % 60:02d}"
        if task.time_window
        else "N/A"
    )
    end_time = (
        f"{task.time_window[1]//60:02d}:{task.time_window[1] % 60:02d}"
        if task.time_window
        else "N/A"
    )
    print(
        f"{start_time} - {end_time} | {pet.name} ({pet.species}) -> {task.name} "
        f"[Priority: {task.priority}]"
    )

total_minutes = sum(task.duration for _, task in today_plan)
print(f"\nScheduled time: {total_minutes}/{DAILY_BUDGET_MINUTES} minutes")

if unscheduled_tasks:
    print("\nUnscheduled Tasks:")
    for pet, task, reason in unscheduled_tasks:
        print(
            f"- {pet.name}: {task.name} ({task.duration} min, priority {task.priority}) -> {reason}"
        )

print("\nPlan Explanation:")
print(scheduler.explain_plan(today_plan))
