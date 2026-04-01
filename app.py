import streamlit as st
from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task
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
    st.success(f"{len(st.session_state.tasks)} task(s) added.")
    st.markdown("### Sorted & Filtered Tasks")

    filter_col, sort_col = st.columns(2)
    with filter_col:
        selected_priorities = st.multiselect(
            "Filter by priority",
            ["high", "medium", "low"],
            default=["high", "medium", "low"],
        )
    with sort_col:
        sort_choice = st.selectbox(
            "Sort tasks by",
            ["Priority (high to low)", "Duration (shortest first)", "Title (A-Z)"],
        )

    filtered_tasks = [t for t in st.session_state.tasks if t["priority"] in selected_priorities]

    if sort_choice == "Priority (high to low)":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks = sorted(
            filtered_tasks,
            key=lambda t: (priority_order[t["priority"]], t["duration_minutes"], t["title"].lower()),
        )
    elif sort_choice == "Duration (shortest first)":
        filtered_tasks = sorted(filtered_tasks, key=lambda t: (t["duration_minutes"], t["title"].lower()))
    else:
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t["title"].lower())

    if not filtered_tasks:
        st.warning("No tasks match the selected filters.")
    else:
        st.table(filtered_tasks)

    st.caption("This table is the polished preview of your sorted and filtered planning data.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate and display today's schedule using your Scheduler class.")

col_start, col_hours = st.columns(2)
with col_start:
    schedule_start = st.time_input("Start time", value=datetime.now().replace(second=0, microsecond=0).time())
with col_hours:
    schedule_hours = st.number_input("Planning window (hours)", min_value=1, max_value=24, value=8)

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(id="owner-1", name=owner_name)
        pet = Pet(id="pet-1", name=pet_name, species=species)

        for index, task_data in enumerate(st.session_state.tasks, start=1):
            pet.add_task(
                Task(
                    id=f"task-{index}",
                    description=task_data["title"],
                    duration_minutes=task_data["duration_minutes"],
                )
            )

        owner.add_pet(pet)
        scheduler = Scheduler()

        today = datetime.now()
        start_dt = datetime.combine(today.date(), schedule_start)
        end_dt = start_dt + timedelta(hours=int(schedule_hours))

        scheduler.assign_times(owner, start_dt, end_dt)
        scheduled_tasks = sorted(
            scheduler.get_today_schedule(),
            key=lambda t: t.scheduled_start or datetime.max,
        )

        if not scheduled_tasks:
            st.info("No tasks could be scheduled in the selected time window.")
        else:
            st.success("Schedule generated.")
            st.markdown("### Planned Tasks")
            table_rows = [
                {
                    "Task": task.description,
                    "Start": task.scheduled_start.strftime("%H:%M") if task.scheduled_start else "-",
                    "End": task.scheduled_end.strftime("%H:%M") if task.scheduled_end else "-",
                    "Duration (min)": task.duration_minutes,
                }
                for task in scheduled_tasks
            ]
            st.table(table_rows)

            st.markdown("### Explanation")
            st.code(scheduler.explain(scheduled_tasks), language="text")

            if scheduler.conflict_warnings:
                st.markdown("### Conflict Warnings")
                for warning in scheduler.conflict_warnings:
                    st.warning(warning)
