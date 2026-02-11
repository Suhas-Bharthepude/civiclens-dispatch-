# CivicLens Dispatch - Testing Guide

## What is Testing?

Testing is writing code that checks if your code works correctly. It's like quality control for software.

## Why Test?

✅ Catch bugs before users do  
✅ Confidence when making changes  
✅ Documentation (tests show how code should work)  
✅ Faster development (automated vs manual testing)  

## Running Tests
```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest tests/test_incidents.py

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app
```

## Test Structure

Every test follows the AAA pattern:
```python
def test_something():
    # ARRANGE - Set up test data
    data = {"field": "value"}
    
    # ACT - Do the thing you're testing
    response = create_something(data)
    
    # ASSERT - Check it worked
    assert response.status_code == 200
```

## Test Files

- `test_basics.py` - Learn pytest fundamentals
- `test_api.py` - Test basic endpoints
- `test_incidents.py` - Test incident CRUD operations

## Writing New Tests

1. Create file starting with `test_`
2. Write functions starting with `test_`
3. Use assertions to check results
4. Run pytest to verify

## Common Assertions
```python
# Equality
assert x == y

# Truthiness
assert is_valid
assert not is_invalid

# Membership
assert item in list

# Type checking
assert isinstance(data, list)

# Exceptions
with pytest.raises(ValueError):
    divide_by_zero()
```

## Test Coverage

Good test coverage means most of your code is tested.
```bash
# Check coverage
pytest --cov=app --cov-report=html

# Open htmlcov/index.html to see visual coverage report
```

## Best Practices

✅ One test per function/feature  
✅ Clear, descriptive test names  
✅ Independent tests (don't rely on each other)  
✅ Fast tests (slow tests won't be run often)  
✅ Test edge cases and errors, not just happy path  

---

*Last updated: Day 20*