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

**Task given to both models:** implement rescheduling logic for weekly recurring tasks — when a weekly task is marked complete, generate the next occurrence due 7 days later and add it back to the pet's task list.

| | Option A — Claude (Sonnet) | Option B — ChatGPT (GPT-4o) |
|-|---------------------------|------------------------------|
| **Model / tool used** | Claude Sonnet via Claude Code | ChatGPT GPT-4o via chat.openai.com |
| **Prompt** | "Based on my Task dataclass with a due_date field, implement next_occurrence() that returns a fresh copy due 7 days later for weekly tasks and 1 day later for daily tasks. It should return None for unknown frequencies." | "I have a Task class with fields: routine_name, frequency, duration, priority, completed, due_date. Write a next_occurrence method that handles daily and weekly recurrence." |
| **Response summary** | Used `FREQUENCY_DAYS` dict + `timedelta`, returned `None` for unknown frequencies, used `date.today()` as fallback when `due_date` is None, kept the original task immutable by constructing a new Task | Used `datetime.strptime` + `strftime` to parse and reformat the date as a string, hardcoded `if frequency == "daily"` / `elif frequency == "weekly"` branches, raised `ValueError` for unknown frequencies |
| **What was useful** | The dict-based dispatch (`FREQUENCY_DAYS`) made adding new frequencies trivial — just add an entry to the dict. The `None` fallback for missing `due_date` was a practical touch. | The if/elif structure was easy to read and understand for a beginner. The ValueError made the failure case explicit rather than silently returning None. |
| **Problems noticed** | Slightly more abstract — the dict pattern requires understanding that `FREQUENCY_DAYS.get(freq)` returns `None` for unknown keys | Used string parsing (`strptime`) on a field that is already a `date` object — unnecessary conversion that would break if `due_date` was stored as a `date` not a string. Also raising `ValueError` instead of returning `None` means callers must always wrap in try/except. |
| **Decision** | Used Claude's approach | Not used |

**Which approach was used and why:**

Claude's version. The `FREQUENCY_DAYS` dict is cleaner than if/elif chains — adding "monthly" later is one line, not a new branch. The `None` return for unknown frequencies is also a better fit for a scheduler that should skip unknown tasks gracefully rather than crash. The main manual correction was confirming that `due_date` is stored as a Python `date` object (not a string), so no parsing was needed — just `timedelta` arithmetic directly.
