📅 Day 20 – Testing Basics with pytest
🎯 What You'll Learn Today
Unit tests and simple API tests
🤔 Why This Matters
Tests show professionalism and help refactor safely. They catch bugs before users do!
💡 How It Applies to CivicLens
Testing incident creation & listing ensures your API works correctly

🧠 Core Concepts Explained (Complete Beginner Level)
What is Testing?
Simple analogy: Testing is like a quality control checklist.
Imagine you're building a toy car:

✅ Do the wheels spin?
✅ Does the door open?
✅ Does it roll straight?

In programming, automated tests are like having a robot that checks your code works correctly every time you make changes.
Why Write Tests?
Without tests:
python# You make a change to your code
# You manually test by:
# 1. Starting the server
# 2. Opening browser
# 3. Clicking through your app
# 4. Checking if everything still works
# This takes 10+ minutes every time!
With tests:
python# You make a change
# Run: pytest
# All tests run in 5 seconds
# ✅ Everything works!
What is pytest?
pytest is a Python testing framework. Think of it as a tool that:

Finds all your test files
Runs each test function
Reports which tests pass ✅ or fail ❌

Types of Tests

Unit Tests: Test one small piece of code in isolation

Example: "Does the add(2, 3) function return 5?"


Integration Tests: Test multiple pieces working together

Example: "Can I create an incident and then retrieve it?"


API Tests: Test your endpoints work correctly

Example: "Does POST /incidents return status code 201?"



Test Structure (AAA Pattern)
Every test follows this pattern:
pythondef test_something():
    # ARRANGE - Set up test data
    incident_data = {"description": "Test", "location": "123 St", "source": "test"}
    
    # ACT - Do the thing you're testing
    response = create_incident(incident_data)
    
    # ASSERT - Check if it worked correctly
    assert response.status_code == 201  # Check status code is 201 (Created)