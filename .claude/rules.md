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

## Python Environment

- **Always use the virtual environment** located at `backend/venv/`
- Activate venv before running any Python commands: `source backend/venv/bin/activate`
- Install packages using pip within the venv
- Never install packages globally
- Keep `backend/requirements.txt` up to date with all dependencies
- When running backend commands, either:
  - Activate venv first: `source backend/venv/bin/activate && python app/main.py`
  - Or use venv Python directly: `backend/venv/bin/python app/main.py`
