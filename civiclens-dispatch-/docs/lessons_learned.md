# Lessons Learned (Days 1-21)

## Technical Lessons

### 1. Environment Variables Are Critical
**What I learned:** Never hardcode secrets in code. Use `.env` files.

**Why it matters:** Accidentally committing passwords to GitHub is a common mistake that can have serious security consequences.

**What I do now:** 
- Always add `.env` to `.gitignore` immediately
- Create `.env.example` as a template
- Use `python-dotenv` to load environment variables

### 2. Async vs Sync Can Be Tricky
**What I learned:** FastAPI is async, but some operations (like SQLAlchemy's `create_all()`) are sync.

**Why it matters:** Mixing async and sync incorrectly causes runtime errors that are hard to debug.

**What I do now:**
- Use async database operations for routes (with `databases` library)
- Use sync engine only for table creation
- For SQLite: `sqlite:///` (sync) vs `sqlite+aiosqlite:///` (async)

### 3. Test Early, Test Often
**What I learned:** Writing tests alongside code is much easier than writing them later.

**Why it matters:** Tests catch bugs immediately and give confidence when refactoring.

**What I do now:**
- Write tests for new endpoints immediately
- Use fixtures for common setup (like database cleanup)
- Run tests before every commit

### 4. File Organization Matters
**What I learned:** Good project structure makes finding code easier.

**Why it matters:** As projects grow, bad organization becomes overwhelming.

**What I do now:**
- Group by feature (routes, schemas, services)
- Keep files focused (one purpose per file)
- Use `__init__.py` to make imports cleaner

### 5. Background Tasks Need Careful Design
**What I learned:** Long-running operations should not block HTTP responses.

**Why it matters:** Users shouldn't wait 30 seconds for an API response.

**What I do now:**
- Use FastAPI's BackgroundTasks for short async operations
- Plan to use Celery + Redis for longer tasks
- Always return response immediately, process in background

## Development Process Lessons

### 6. Git Commits Should Be Meaningful
**What I learned:** Good commit messages help understand project history.

**Bad:** `git commit -m "fixed stuff"`  
**Good:** `git commit -m "Fix database connection error in SQLite async mode"`

**What I do now:**
- Use descriptive commit messages
- Commit after completing each feature
- Use branches for major changes (once I learn branching better)

### 7. Documentation Saves Time
**What I learned:** "I'll remember this" is a lie. You won't remember.

**Why it matters:** Coming back to code after a week without docs is confusing.

**What I do now:**
- Document as I build
- Explain *why* not just *what*
- Keep README updated

### 8. Reading Error Messages Carefully
**What I learned:** Error messages usually tell you exactly what's wrong.

**Example:** 
```
ModuleNotFoundError: No module named 'app'
```
This means pytest can't find the `app` module - probably wrong directory.

**What I do now:**
- Read the entire error message
- Look at the stack trace to find where error occurred
- Google the specific error message

### 9. Defaults Should Be Sensible
**What I learned:** Configuration should work with minimal setup.

**Example:**
```python
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
```
Falls back to SQLite if PostgreSQL not configured.

**What I do now:**
- Provide sensible defaults for optional settings
- Require explicit values only for critical settings
- Make it easy to get started

### 10. Tests Are Documentation Too
**What I learned:** Tests show how code is meant to be used.

**Example:**
```python
def test_create_incident():
    # This test shows exactly how to create an incident
    incident_data = {
        "source": "citizen",
        "description": "Fire on Main St",
        "location": "123 Main St"
    }
    response = client.post("/incidents", json=incident_data)
    assert response.status_code == 201
```

**What I do now:**
- Write clear, readable tests
- Use tests as usage examples
- Name tests descriptively

## Tools & Technologies Lessons

### 11. Virtual Environments Are Essential
**What I learned:** Never install packages globally. Always use a venv.

**Why it matters:** Different projects need different package versions.

**What I do now:**
- Create venv for every project
- Always activate venv before running code
- Add venv to `.gitignore`

### 12. FastAPI is Amazing
**What I learned:** FastAPI's automatic API docs and validation are huge time-savers.

**Why it matters:** `/docs` endpoint provides instant, interactive API documentation.

**What I do now:**
- Use Pydantic models for automatic validation
- Rely on auto-generated OpenAPI docs
- Appreciate async support

### 13. SQLite is Great for Development
**What I learned:** Don't need PostgreSQL running for local development.

**Why it matters:** SQLite is just a file - no server setup needed.

**What I do now:**
- Use SQLite for development
- Plan to use PostgreSQL for production
- Keep database operations compatible with both

## Mistakes I Made (And Fixed)

### 14. Creating Duplicate Directories
**Mistake:** Created `backend/backend/` instead of just `backend/`

**Why it happened:** Confusion about where to run commands.

**How I fixed:** Moved files to correct location, deleted duplicate.

**Lesson:** Always check `pwd` (current directory) before creating folders.

### 15. Empty Test Files
**Mistake:** Created test files but didn't add any content.

**Why it happened:** Created the structure but forgot to fill it in.

**How I fixed:** Added test functions to each file.

**Lesson:** Create *and test* immediately, don't leave placeholders.

### 16. Not Checking File Sizes
**Mistake:** Wondered why tests weren't running when files were 0 bytes.

**Why it happened:** Didn't verify files had content.

**How I fixed:** `ls -lh` shows file sizes - use it to check.

**Lesson:** Verify your changes actually happened.

## Productivity Lessons

### 17. Take Breaks
**What I learned:** Staring at code for hours doesn't help.

**Why it matters:** Fresh eyes spot problems immediately.

**What I do now:**
- Take breaks every hour
- Walk away from difficult problems
- Come back with fresh perspective

### 18. Google Is Your Friend
**What I learned:** Everyone Googles error messages, even experts.

**Why it matters:** You don't need to memorize everything.

**What I do now:**
- Search for error messages
- Read Stack Overflow
- Check official docs
- Don't feel bad about not knowing everything

### 19. Comment While Writing, Not Later
**What I learned:** "I'll add comments later" means never.

**Why it matters:** You understand code best while writing it.

**What I do now:**
- Write comments as I code
- Explain *why*, not just *what*
- Make comments useful to future me

### 20. Commit Often
**What I learned:** Small, frequent commits are better than huge ones.

**Why it matters:** Easy to undo small changes, hard to untangle big commits.

**What I do now:**
- Commit after each feature
- One logical change per commit
- Can easily revert if something breaks

## What's Next

### Days 22-30: Frontend
I'll learn:
- React basics
- Component architecture
- State management
- API integration

### Days 31+: Real AI
I'll learn:
- Hugging Face models
- Model selection
- API vs local hosting
- Error handling for AI

---

*These lessons will evolve as I continue learning!*