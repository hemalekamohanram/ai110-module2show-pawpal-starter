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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

tasks moved from Schedule/Scheduler into Pet. That's the key design change that happened during implementation.     

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

the conflict detector only flags tasks that share the exact same start_time string.
it doesn't check whether two tasks overlap in duration — so if one task starts at 07:00 for 30 min and another starts at 07:15 for 20 min, no warning fires even though they run at the same time.

that's a reasonable tradeoff here because:
- most conflicts a pet owner creates are accidental exact matches (accidentally typing the same time twice)
- overlap detection would need to convert "HH:MM" to minutes, sort the list, and compare time windows — more code for an edge case that rarely happens in a small personal schedule
- the scheduler is meant to give a heads-up, not enforce hard rules, so catching the obvious case is enough for now

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
