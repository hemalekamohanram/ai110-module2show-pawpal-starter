import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — acts as the app's "memory" across reruns.
# We only create the Owner once; every button click after that reads from here.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet setup
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
# Section 2: Add tasks — only shown once an owner exists
# ---------------------------------------------------------------------------
if st.session_state.owner is not None:
    owner = st.session_state.owner
    pets = owner.get_pets()

    st.subheader("Step 2 — Add Tasks")

    pet_names = [p.get_name() for p in pets]
    selected_pet_name = st.selectbox("Add task to", pet_names)
    selected_pet = next(p for p in pets if p.get_name() == selected_pet_name)

    priority_map = {"low": 1, "medium": 2, "high": 3}

    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        task = Task(
            routine_name=task_name,
            frequency="daily",
            duration=int(duration),
            priority=priority_map[priority_label],
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task_name}' to {selected_pet_name}")

    # Show current tasks per pet
    for pet in pets:
        tasks = pet.get_tasks()
        if tasks:
            st.markdown(f"**{pet.get_name()}'s tasks:**")
            st.table([
                {
                    "Task": t.get_routine_name(),
                    "Duration (min)": t.get_duration(),
                    "Priority": {1: "low", 2: "medium", 3: "high"}[t.get_priority()],
                }
                for t in tasks
            ])

    st.divider()

    # ---------------------------------------------------------------------------
    # Section 3: Generate schedule
    # ---------------------------------------------------------------------------
    st.subheader("Step 3 — Generate Schedule")

    available_time = st.number_input(
        "Available time today (minutes)", min_value=10, max_value=480, value=90
    )

    if st.button("Generate schedule"):
        scheduler = Scheduler(owner=owner, available_time=int(available_time))
        plan = scheduler.generate()

        if not plan:
            st.warning("No tasks fit in the available time. Try adding shorter tasks or increasing available time.")
        else:
            st.success(f"Today's plan for {owner.get_name()}'s pets")
            start_hour, start_min = 8, 0
            rows = []
            for task in plan:
                time_str = f"{start_hour:02d}:{start_min:02d}"
                priority_label = {1: "low", 2: "medium", 3: "high"}[task.get_priority()]
                rows.append({
                    "Time": time_str,
                    "Task": task.get_routine_name(),
                    "Duration (min)": task.get_duration(),
                    "Priority": priority_label,
                })
                start_min += task.get_duration()
                start_hour += start_min // 60
                start_min %= 60

            st.table(rows)

            total = scheduler.get_total_duration(plan)
            st.caption(
                f"Scheduled {len(plan)} of {len(scheduler.get_all_tasks())} tasks "
                f"— {total} / {available_time} min used"
            )

else:
    st.info("Fill in owner and pet info above, then click **Save owner & pet** to get started.")
