# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

**What task did you give the agent?**

add a third algorithmic capability — urgency-weighted prioritization — that combines task priority and due_date closeness into a single score, then use that score to build a smarter daily plan

**What did the agent do?**

files modified:
- `pawpal_system.py` — added `weighted_sort()` and `weighted_generate()` to Scheduler
- `tests/test_pawpal.py` — added 4 tests covering the new methods

steps taken:
1. read pawpal_system.py and the existing test file to understand current structure
2. designed the scoring formula: `priority × (1 + 1/(days_until_due + 1))`
3. added `weighted_sort()` with full docstring explaining the math with examples
4. added `weighted_generate()` that reuses weighted_sort() instead of duplicating logic
5. added tests for: due-today beats due-later at same priority, no due_date falls back to plain priority, urgent medium-priority beats calm high-priority, available time is still respected
6. ran pytest — 38/38 passed

**What did you have to verify or fix manually?**

- confirmed the score formula made intuitive sense before committing — checked: priority 2 due today (score 4.0) should beat priority 3 with no due_date (score 3.0), which it does
- checked that `weighted_generate()` didn't duplicate the greedy loop logic and instead called `weighted_sort()` directly — cleaner that way
- verified tests covered the non-obvious case (urgent medium beats calm high) not just the obvious ones

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
