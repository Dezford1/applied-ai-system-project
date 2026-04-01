import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler


def format_time_window(task: Task) -> str:
    """Return a user-friendly time window string for a task."""
    if not task.time_window:
        return "N/A"
    start, end = task.time_window
    return f"{start//60:02d}:{start%60:02d}-{end//60:02d}:{end%60:02d}"


def tasks_to_rows(task_items):
    """Convert (pet, task) tuples into table-friendly dict rows."""
    rows = []
    for pet, task in task_items:
        rows.append(
            {
                "Pet": pet.name,
                "Task": task.name,
                "Type": task.type,
                "Duration (min)": task.duration,
                "Priority": task.priority,
                "Time": format_time_window(task),
                "Completed": "Yes" if task.completed else "No",
            }
        )
    return rows

# ------------------------
# Persistent Owner in session_state
# ------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Dezmond", "dezmond@example.com")

# ------------------------
# Persistent Scheduler in session_state
# ------------------------
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

# For convenience, assign local variables
owner = st.session_state.owner
scheduler = st.session_state.scheduler 

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ------------------------
# Quick Demo Inputs (UI only)
# ------------------------
st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ------------------------
# Add Pet Section (wired to backend)
# ------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    pet_name_input = st.text_input("Pet Name")
    species_input = st.selectbox("Species", ["dog", "cat", "other"])
    age_input = st.number_input("Age", min_value=0, max_value=30, value=1)
    submitted_pet = st.form_submit_button("Add Pet")
    
    if submitted_pet and pet_name_input:
        new_pet = Pet(pet_name_input, species_input, age_input)
        owner.add_pet(new_pet)
        st.success(f"Added pet '{pet_name_input}'!")

# Display current pets from backend
if owner.pets:
    st.subheader("Current Pets:")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species}, {pet.age} yrs)")

st.divider()

# ------------------------
# Add Task Section (wired to backend)
# ------------------------
if owner.pets:
    st.subheader("Add a Task")
    pet_options = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Select Pet", pet_options)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    with st.form("add_task_form"):
        task_name_input = st.text_input("Task Name")
        task_type_input = st.selectbox("Type", ["feeding", "walk", "medication", "grooming", "enrichment"])
        duration_input = st.number_input("Duration (minutes)", min_value=1, value=10)
        priority_input = st.number_input("Priority (1=high)", min_value=1, max_value=5, value=1)
        has_time_window = st.checkbox("Set time window", value=False)

        if has_time_window:
            start_hour = st.number_input("Start hour (0-23)", min_value=0, max_value=23, value=8)
            start_minute = st.number_input("Start minute (0-59)", min_value=0, max_value=59, value=0)
            end_hour = st.number_input("End hour (0-23)", min_value=0, max_value=23, value=9)
            end_minute = st.number_input("End minute (0-59)", min_value=0, max_value=59, value=0)
        submitted_task = st.form_submit_button("Add Task")

        if submitted_task and task_name_input:
            time_window = None
            if has_time_window:
                start_total = int(start_hour) * 60 + int(start_minute)
                end_total = int(end_hour) * 60 + int(end_minute)

                if end_total <= start_total:
                    st.error("Time window must end after it starts.")
                    st.stop()

                time_window = (start_total, end_total)

            new_task = Task(
                task_name_input,
                task_type_input,
                int(duration_input),
                int(priority_input),
                time_window=time_window,
            )
            selected_pet.add_task(new_task)
            st.success(f"Added task '{task_name_input}' to {selected_pet.name}")

# ------------------------
# Display Current Tasks
# ------------------------
st.subheader("Current Tasks")
all_tasks = scheduler.get_all_tasks(owner)

if all_tasks:
    selected_filter_pet = st.selectbox(
        "Filter by pet",
        ["All pets"] + [pet.name for pet in owner.pets],
    )
    selected_filter_status = st.selectbox(
        "Filter by status",
        ["All", "Incomplete", "Completed"],
    )

    filter_pet = None if selected_filter_pet == "All pets" else selected_filter_pet
    if selected_filter_status == "Incomplete":
        filter_completed = False
    elif selected_filter_status == "Completed":
        filter_completed = True
    else:
        filter_completed = None

    filtered_tasks = scheduler.filter_tasks(
        all_tasks,
        pet_name=filter_pet,
        completed=filter_completed,
    )
    sorted_filtered_tasks = scheduler.sort_by_time(filtered_tasks)

    st.table(tasks_to_rows(sorted_filtered_tasks))
else:
    st.info("No tasks yet. Add a task to see it here.")

st.divider()

# ------------------------
# Generate Daily Schedule
# ------------------------
st.subheader("Build Schedule")
daily_budget_minutes = st.number_input(
    "Daily time budget (minutes)",
    min_value=1,
    max_value=1440,
    value=60,
)

if st.button("Generate schedule"):
    all_tasks = scheduler.get_all_tasks(owner)
    incomplete_tasks = scheduler.filter_tasks(all_tasks, completed=False)

    conflict_warnings = scheduler.detect_conflict_warnings(incomplete_tasks)
    for warning in conflict_warnings:
        st.warning(warning)

    scheduled, unscheduled = scheduler.build_budgeted_plan(
        incomplete_tasks,
        int(daily_budget_minutes),
    )

    if scheduled:
        st.success(f"Scheduled {len(scheduled)} task(s) for today.")
        st.table(tasks_to_rows(scheduled))
        st.caption("Plan explanation")
        st.text(scheduler.explain_plan(scheduled))
    else:
        st.info("No tasks scheduled for today.")

    if unscheduled:
        unscheduled_rows = []
        for pet, task, reason in unscheduled:
            unscheduled_rows.append(
                {
                    "Pet": pet.name,
                    "Task": task.name,
                    "Reason": reason,
                    "Duration (min)": task.duration,
                    "Priority": task.priority,
                }
            )
        st.warning("Some tasks could not be scheduled.")
        st.table(unscheduled_rows)
