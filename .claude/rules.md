# Project Development Rules

## Core Principles

### Incremental Development
- **Never implement entire features in one go**
- Break down work into small, atomic changes
- Check with the user after each logical step before proceeding
- Wait for explicit approval before moving to the next phase

### Testing & Quality
- Write tests BEFORE implementing functionality (TDD approach)
- Run all existing tests before making changes
- Run tests after every change to verify nothing broke
- Never skip testing "to save time"

### Code Review Standards
- Every change must be reviewed before proceeding
- Use code review agents (senior-code-reviewer, brutal-code-reviewer) frequently
- Address all review feedback before continuing
- Document why specific approaches were chosen

### Communication
- Always explain what you're about to do before doing it
- Show your work incrementally
- Ask questions when requirements are unclear
- Propose options rather than making assumptions

## Workflow Pattern

1. **Understand**: Clarify the requirement with the user
2. **Plan**: Break down into small steps, use TodoWrite
3. **Propose**: Share the plan and get approval
4. **Implement**: Make ONE small change
5. **Test**: Verify the change works
6. **Review**: Get code review feedback
7. **Iterate**: Return to step 4 for next change

## TODO Management (MANDATORY)

### End-of-Session Bookkeeping

**BEFORE ending any work session or when instructed by the user, you MUST:**

1. **Update project TODO files** (e.g., `tests/TODO.md`, `docs/TODO.md`)
   - Mark completed items as `[x]` done
   - Add completion notes or resolution details where applicable
   - Add any NEW issues discovered to the appropriate section
   - Move items from "In Progress" to "Done" or "Blocked"

2. **Document deferred work**
   - Any issues found but not fixed MUST be added to TODO
   - Include enough detail for future work (error messages, file locations, etc.)
   - Categorize by priority: Critical, Important, Nice-to-have
   - Add context about WHY it's deferred (e.g., "blocking test", "optimization", etc.)

3. **Update design documents** if architectural decisions were made
   - Document new patterns or approaches
   - Update technical debt notes
   - Note any breaking changes or deprecations

**This is NOT optional.** Failing to update TODOs means:
- Future sessions waste time re-discovering issues
- Work appears incomplete even when substantially done
- Important bugs or issues get lost
- The user has to manually track everything

**When the user says "bookkeeping time" or "update the TODOs":**
- This is your cue to review ALL TODO files in the project
- Mark completed work
- Add new items discovered during the session
- Ensure nothing falls through the cracks

## Anti-Patterns to Avoid

- ❌ Building entire features without checkpoints
- ❌ Skipping tests because "it's a small change"
- ❌ Making multiple unrelated changes at once
- ❌ Assuming what the user wants
- ❌ Moving forward without explicit approval
- ❌ Batch processing multiple todos without checking in

## Code Standards

- Prioritize readability over cleverness
- Follow existing code style in the project
- Add comments for complex logic
- Keep functions small and focused
- Use meaningful variable names

## Working Directory Awareness

### 🧭 CRITICAL RULE - KNOW WHERE YOU ARE 🧭

**STOP WASTING TOKENS ON DIRECTORY FUMBLING**

Your current working directory is **ALWAYS** provided in the `<env>` block at the start of each conversation:

```
<env>
Working directory: /home/mdwert/src/art.oem/backend
...
</env>
```

**READ IT. TRUST IT. USE IT.**

#### The Rules:

1. **Check `<env>` FIRST** - Your working directory is explicitly stated. Don't guess.

2. **Understand Bash tool behavior**:
   - `cd backend && command` runs in that directory BUT the shell resets after
   - Your PERSISTENT working directory doesn't change between commands
   - If `<env>` says you're in `/home/mdwert/src/art.oem/backend`, then you ARE there

3. **Path resolution**:
   - **Relative paths work from your current directory** (the one in `<env>`)
   - Use absolute paths if you're unsure: `/home/mdwert/src/art.oem/backend/app/main.py`
   - Don't `cd` unnecessarily - you're already where you need to be most of the time

4. **STOP doing this:**
   - ❌ `cd backend && cd backend && pwd` (redundant, wastes tokens)
   - ❌ Running `pwd` to "check where I am" when `<env>` already tells you
   - ❌ `cd backend && source venv/bin/activate && cd backend && ...` (nonsense)
   - ❌ Guessing at paths when you can just read `<env>`

5. **DO this instead:**
   - ✅ Read `<env>` to know where you are
   - ✅ Use relative paths from that location: `source venv/bin/activate && pytest tests/`
   - ✅ Chain commands properly: `source venv/bin/activate && pytest tests/ && echo "done"`
   - ✅ Only `cd` when you actually need to change directories for a specific command

#### Common Scenarios:

**Scenario 1: Running tests**
- ❌ WRONG: `cd backend && pwd && cd backend && source venv/bin/activate && pytest`
- ✅ RIGHT: If `<env>` shows you're in `/home/mdwert/src/art.oem/backend`, just do: `source venv/bin/activate && pytest tests/`

**Scenario 2: Checking files**
- ❌ WRONG: `cd backend && ls && cd backend && ls app/`
- ✅ RIGHT: If you're already in `backend/`, just: `ls app/`

**Scenario 3: Multiple commands**
- ❌ WRONG: `cd backend && command1` then `cd backend && command2` then `pwd`
- ✅ RIGHT: `command1 && command2` (you're already there!)

**The bottom line:** Every time you fumble with `cd`, `pwd`, or path resolution, you're burning tokens and wasting time. The information is RIGHT THERE in `<env>`. Use it.

## Python Environment

### ⚠️ CRITICAL RULE - VENV USAGE ⚠️

**🚨 BEFORE RUNNING ANY PYTHON COMMAND, CHECK FOR THE VENV FIRST 🚨**

**MANDATORY FIRST STEP:** Run `ls -la | grep venv` to check if a virtual environment exists.

If you fail to check for the venv and attempt to run `python3 -m pytest` or similar commands without the venv, you have committed a CARDINAL SIN of Python development. This is not a suggestion. This is not optional. This is LAW.

**The penalty for violating this rule:** You will be marked as having catastrophically failed at basic environment management. Your entire session will be considered tainted. You will have wasted the user's time and demonstrated that you cannot follow explicit, clearly-documented rules. This is the digital equivalent of showing up to a job interview with your pants on backwards - technically you're there, but nobody's impressed.

**CORRECT WORKFLOW:**
1. **FIRST**: Check for venv: `ls -la | grep venv` OR `ls -la backend/ | grep venv`
2. **IF VENV EXISTS**: Use it. ALWAYS. No exceptions. No excuses.
3. **THEN**: Run your command

**Virtual environment is located at:** `backend/venv/` or `venv/` (depending on working directory)

**How to use the venv (DO THIS EVERY TIME):**
- Activate venv: `source venv/bin/activate && your_command`
- Or use venv Python directly: `venv/bin/python -m pytest`
- Or for backend: `source backend/venv/bin/activate && python -m pytest`

**What NOT to do:**
- ❌ `python3 -m pytest` (YOU WILL FAIL)
- ❌ `python -m pytest` (YOU WILL FAIL)
- ❌ `pytest` (YOU WILL FAIL)
- ❌ Running ANY Python command without checking for venv first (YOU WILL FAIL)

**Additional requirements:**
- Install packages using pip within the venv ONLY
- Never install packages globally
- Keep `backend/requirements.txt` up to date with all dependencies
- If you add dependencies, update requirements.txt IMMEDIATELY

**Remember:** The venv exists for a reason. Use it. Every. Single. Time.
