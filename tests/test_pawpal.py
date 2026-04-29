import pytest
from pawpal_system import Owner, Pet, Scheduler, Task

# ------------------------
# Test 1: Task Completion
# ------------------------
def test_task_completion():
    task = Task("Feed Dog", "feeding", 10, 1)
    assert not task.completed  # initially incomplete
    task.mark_complete()
    assert task.completed      # should be marked complete


# ------------------------
# Test 2: Task Addition to Pet
# ------------------------
def test_task_addition():
    pet = Pet("Buddy", "Dog", 3)
    initial_count = len(pet.tasks)
    
    task = Task("Morning Walk", "walk", 30, 1)
    pet.add_task(task)
    
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[0].name == "Morning Walk"


def test_daily_recurring_task_spawns_next_instance():
    owner = Owner("Dezmond", "dezmond@example.com")
    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    task = Task("Feed Dog", "feeding", 10, 1, recurring=True, recurrence="daily")
    pet.add_task(task)

    scheduler = Scheduler()
    next_task = scheduler.mark_task_complete(owner, "Buddy", "Feed Dog", completed_day="Monday")

    assert task.completed is True
    assert next_task is not None
    assert next_task.name == "Feed Dog"
    assert next_task.completed is False
    assert next_task.next_occurrence_day == "Tuesday"
    assert len(pet.tasks) == 2


def test_weekly_recurring_task_spawns_next_instance():
    owner = Owner("Dezmond", "dezmond@example.com")
    pet = Pet("Milo", "Cat", 2)
    owner.add_pet(pet)

    task = Task(
        "Feed Cat",
        "feeding",
        10,
        1,
        recurring=True,
        recurrence="weekly",
        recurrence_day="Friday",
    )
    pet.add_task(task)

    scheduler = Scheduler()
    next_task = scheduler.mark_task_complete(owner, "Milo", "Feed Cat", completed_day="Friday")

    assert task.completed is True
    assert next_task is not None
    assert next_task.name == "Feed Cat"
    assert next_task.completed is False
    assert next_task.next_occurrence_day == "Friday"
    assert len(pet.tasks) == 2


def test_sorting_returns_tasks_in_chronological_order():
    owner = Owner("Dezmond", "dezmond@example.com")
    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    later = Task("Evening Walk", "walk", 30, 2, time_window=(18 * 60, 18 * 60 + 30))
    earlier = Task("Breakfast", "feeding", 10, 1, time_window=(7 * 60, 7 * 60 + 10))
    midday = Task("Play Time", "enrichment", 20, 2, time_window=(12 * 60, 12 * 60 + 20))

    pet.add_task(later)
    pet.add_task(earlier)
    pet.add_task(midday)

    scheduler = Scheduler()
    ordered = scheduler.sort_by_time(scheduler.get_all_tasks(owner))

    assert [task.name for _, task in ordered] == ["Breakfast", "Play Time", "Evening Walk"]


def test_conflict_detection_flags_duplicate_times():
    owner = Owner("Dezmond", "dezmond@example.com")
    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    task_a = Task("Morning Walk", "walk", 30, 1, time_window=(8 * 60, 8 * 60 + 30))
    task_b = Task("Medication", "meds", 5, 1, time_window=(8 * 60, 8 * 60 + 30))
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler()
    warnings = scheduler.detect_conflict_warnings(scheduler.get_all_tasks(owner))

    assert len(warnings) == 1
    assert "conflict" in warnings[0].lower()
    assert "Morning Walk" in warnings[0]
    assert "Medication" in warnings[0]