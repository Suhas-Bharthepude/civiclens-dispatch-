# backend/tests/test_basics.py
# This file contains basic tests to learn pytest fundamentals

# ========================================
# LESSON 1: Your First Test
# ========================================

def test_simple_math():
    """
    This is the simplest test possible.
    It tests if Python can do basic math.
    
    The name MUST start with 'test_' for pytest to find it.
    """
    # ARRANGE: Set up the data we need
    x = 2
    y = 3
    
    # ACT: Do the calculation
    result = x + y
    
    # ASSERT: Check if result is correct
    # If this is True, test passes ✅
    # If this is False, test fails ❌
    assert result == 5


def test_string_operations():
    """
    Test that string concatenation works.
    This teaches you how assert works.
    """
    # ARRANGE
    first_name = "John"
    last_name = "Doe"
    
    # ACT
    full_name = first_name + " " + last_name
    
    # ASSERT
    assert full_name == "John Doe"  # Check if concatenation worked
    assert len(full_name) == 8  # Check if length is correct


def test_lists():
    """
    Test that list operations work.
    Shows you can have multiple asserts in one test.
    """
    # ARRANGE
    my_list = [1, 2, 3]
    
    # ACT
    my_list.append(4)
    
    # ASSERT
    assert len(my_list) == 4  # Check length increased
    assert my_list[-1] == 4  # Check last item is 4
    assert 2 in my_list  # Check 2 is in the list


# ========================================
# LESSON 2: Testing Functions
# ========================================

def add_numbers(a, b):
    """
    A simple function we want to test.
    This is NOT a test - it's the actual function.
    """
    return a + b


def test_add_numbers():
    """
    This tests the add_numbers function above.
    We test multiple scenarios (called test cases).
    """
    # Test case 1: Positive numbers
    assert add_numbers(2, 3) == 5
    
    # Test case 2: Negative numbers
    assert add_numbers(-1, -1) == -2
    
    # Test case 3: Zero
    assert add_numbers(0, 5) == 5
    
    # Test case 4: Large numbers
    assert add_numbers(1000, 2000) == 3000


# ========================================
# LESSON 3: Testing Errors (Expected Failures)
# ========================================

def divide(a, b):
    """
    Function that divides two numbers.
    Will raise error if dividing by zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def test_divide_normal():
    """
    Test that division works normally.
    """
    result = divide(10, 2)
    assert result == 5


def test_divide_by_zero():
    """
    Test that dividing by zero raises the correct error.
    
    We EXPECT this to fail, and we test that it fails correctly.
    This uses pytest.raises() context manager.
    """
    # Import pytest to use its special features
    import pytest
    
    # We expect a ValueError to be raised
    # If ValueError IS raised, test passes ✅
    # If ValueError is NOT raised, test fails ❌
    with pytest.raises(ValueError):
        divide(10, 0)
