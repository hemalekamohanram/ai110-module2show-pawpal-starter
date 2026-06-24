# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
core actions:
add information of a pet
create and edit task
generate schedule
display schedule
- What classes did you include, and what responsibilities did you assign to each?
main objects:
owner -> 
    variables: name, list of pets
    action: get name, add pet, get all tasks across pets
pet -> 
    variables: name, species, list of tasks
    action: get name, add task, remove task, get tasks
task -> 
    variables: routine name, frequency, duration, priority, completed
    action: get duration, get frequency, get routine name, get priority, mark complete
scheduler -> 
    variables: owner, available time
    action: get all tasks, generate daily plan, get total duration


**b. Design changes**

yes — tasks moved from Scheduler into Pet
initially i had the scheduler holding the task list but it made more sense for pet to own its tasks and let the scheduler just ask the owner to collect them
also renamed Schedule to Scheduler to make it clear its a logic class not a data class

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

constraints: available time in minutes, task priority (1-3), task duration
time mattered most because without it the schedule is useless — you cant plan around a limit that doesnt exist
priority came second so high urgency tasks like meds always get in before low ones like grooming

**b. Tradeoffs**

the conflict detector only flags tasks that share the exact same start_time string.
it doesn't check whether two tasks overlap in duration — so if one task starts at 07:00 for 30 min and another starts at 07:15 for 20 min, no warning fires even though they run at the same time.

that's a reasonable tradeoff here because:
- most conflicts a pet owner creates are accidental exact matches (accidentally typing the same time twice)
- overlap detection would need to convert "HH:MM" to minutes, sort the list, and compare time windows — more code for an edge case that rarely happens in a small personal schedule
- the scheduler is meant to give a heads-up, not enforce hard rules, so catching the obvious case is enough for now

---

## 3. AI Collaboration

**a. How you used AI**

used AI for brainstorming class design, generating skeletons, writing tests, and explaining why things failed
most helpful prompts were specific ones — attaching the file and asking about one thing at a time
asking "why is this failing" worked better than asking "fix this"

most effective features:
- attaching files so the AI had full context before suggesting anything
- using separate chat sessions for design vs testing vs UI — kept each session focused
- asking the AI to explain test code before saving it so i understood what i was committing

**b. Judgment and verification**

AI suggested writing detect_conflicts as a one-liner list comprehension that combined filtering, formatting, and sorting all in one expression
i rejected it because even though it worked, it was hard to read and harder to debug
kept it as a regular loop with clear variable names — readability matters more than being clever
verified by running the tests and making sure the output messages still made sense

---

## 4. Testing and Verification

**a. What you tested**

tested: mark_complete, add/remove task, generate with edge cases, sort_by_time, filter_by_pet, filter_by_status, detect_conflicts, next_occurrence, mark_task_complete
these were important because the scheduler is the whole point of the app — if generate or recurrence breaks the app is useless

**b. Confidence**

4/5 — core logic is solid and 34 tests all pass
not fully confident about the UI layer since there are no streamlit integration tests
next edge cases to test: overlap detection (tasks that span the same time window), owner with 5+ pets, task with same name across different pets

---

## 5. Reflection

**a. What went well**

the scheduler logic — generate, sort, filter, and conflict detection all work cleanly and are backed by tests
the class design ended up simple and readable which made connecting it to streamlit straightforward

**b. What you would improve**

would add overlap detection to conflict checking (not just exact time matches)
would also add a way to edit or delete tasks from the UI instead of just adding

**c. Key takeaway**

AI is fast at generating code but it doesnt know what you actually want — you have to tell it clearly and check what it gives back
being the lead architect means deciding which suggestions to keep, which to change, and which to throw out entirely
the AI wrote the code but every design decision was mine
