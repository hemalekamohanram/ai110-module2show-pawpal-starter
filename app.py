import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

PRIORITY_MAP   = {"low": 1, "medium": 2, "high": 3}
PRIORITY_LABEL = {1: "low", 2: "medium", 3: "high"}

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Step 1 — Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Step 1 — Owner & Pet Info")

col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
with col3:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save owner & pet"):
    owner = Owner(name=owner_name)
    pet = Pet(name=pet_name, species=species)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.success(f"Saved! Owner: {owner_name} | Pet: {pet_name} ({species})")

st.divider()

# ---------------------------------------------------------------------------
# Steps 2 & 3 only shown once an owner exists
# ---------------------------------------------------------------------------
if st.session_state.owner is None:
    st.info("Fill in owner and pet info above, then click **Save owner & pet** to get started.")
    st.stop()

owner = st.session_state.owner
pets  = owner.get_pets()

# ---------------------------------------------------------------------------
# Step 2 — Add Tasks
# ---------------------------------------------------------------------------
st.subheader("Step 2 — Add Tasks")

pet_names    = [p.get_name() for p in pets]
sel_pet_name = st.selectbox("Add task to", pet_names)
sel_pet      = next(p for p in pets if p.get_name() == sel_pet_name)

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_name = st.text_input("Task name", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    start_time_input = st.text_input("Start time (HH:MM)", value="", placeholder="e.g. 08:00")

if st.button("Add task"):
    task = Task(
        routine_name=task_name,
        frequency="daily",
        duration=int(duration),
        priority=PRIORITY_MAP[priority_label],
        start_time=start_time_input.strip() or None,
    )
    sel_pet.add_task(task)
    st.success(f"Added '{task_name}' to {sel_pet_name}")

# Show current tasks per pet
for pet in pets:
    tasks = pet.get_tasks()
    if tasks:
        st.markdown(f"**{pet.get_name()}'s tasks**")
        st.table([
            {
                "Task":          t.get_routine_name(),
                "Duration (min)": t.get_duration(),
                "Priority":      PRIORITY_LABEL[t.get_priority()],
                "Start time":    t.start_time or "—",
                "Done":          "yes" if t.is_completed() else "no",
            }
            for t in tasks
        ])

st.divider()

# ---------------------------------------------------------------------------
# Step 3 — Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("Step 3 — Generate Schedule")

available_time = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=480, value=90
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner, available_time=int(available_time))
    plan      = scheduler.generate()
    all_tasks = scheduler.get_all_tasks()
    skipped   = [t for t in all_tasks if t not in plan]

    if not plan:
        st.warning("No tasks fit in the available time. Try adding shorter tasks or increasing available time.")
    else:
        # Assign start times to every planned task so sort & conflict detection work
        start_hour, start_min = 8, 0
        for task in plan:
            task.start_time = f"{start_hour:02d}:{start_min:02d}"
            start_min  += task.get_duration()
            start_hour += start_min // 60
            start_min  %= 60

        # Sort chronologically and display
        sorted_plan = scheduler.sort_by_time(plan)

        st.success(f"Today's plan for {owner.get_name()}'s pets — {scheduler.get_total_duration(plan)} / {available_time} min used")
        st.table([
            {
                "Time":          t.start_time,
                "Task":          t.get_routine_name(),
                "Duration (min)": t.get_duration(),
                "Priority":      PRIORITY_LABEL[t.get_priority()],
            }
            for t in sorted_plan
        ])
        st.caption(f"Scheduled {len(plan)} of {len(all_tasks)} tasks.")

        # Conflict warnings
        conflicts = scheduler.detect_conflicts(plan)
        if conflicts:
            st.markdown("#### Scheduling Conflicts")
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("No scheduling conflicts detected.")

        # Skipped tasks
        if skipped:
            with st.expander(f"Skipped tasks ({len(skipped)}) — didn't fit in available time"):
                st.table([
                    {
                        "Task":          t.get_routine_name(),
                        "Duration (min)": t.get_duration(),
                        "Priority":      PRIORITY_LABEL[t.get_priority()],
                    }
                    for t in skipped
                ])

st.divider()

# ---------------------------------------------------------------------------
# Step 4 — Task Status Filter
# ---------------------------------------------------------------------------
st.subheader("Step 4 — View Tasks by Status")

scheduler = Scheduler(owner=owner, available_time=0)
col1, col2 = st.columns(2)

with col1:
    pending = scheduler.filter_by_status(completed=False)
    st.markdown(f"**Pending ({len(pending)})**")
    if pending:
        st.table([{"Task": t.get_routine_name(), "Priority": PRIORITY_LABEL[t.get_priority()]} for t in pending])
    else:
        st.info("All tasks completed!")

with col2:
    done = scheduler.filter_by_status(completed=True)
    st.markdown(f"**Completed ({len(done)})**")
    if done:
        st.table([{"Task": t.get_routine_name(), "Priority": PRIORITY_LABEL[t.get_priority()]} for t in done])
    else:
        st.info("No completed tasks yet.")
