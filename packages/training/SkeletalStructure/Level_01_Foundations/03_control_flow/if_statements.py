"""
Skeletal Exercise: Python If Statements
Level: 1 - Foundations
Topic: Control Flow
Difficulty: 1/5
Duration: 15 minutes

Learning Objectives:
- Understand if/elif/else syntax
- Practice comparison operators
- Learn logical operators (and, or, not)

Instructions:
Complete the TODOs to implement conditional logic.
"""


# TODO 1: Implement grading logic for check_grade
def check_grade(score: int) -> str:
    """
    Determine letter grade based on numeric score.

    Args:
        score: Numeric score (0-100)

    Returns:
        Letter grade (A, B, C, D, F)

    TODO 1: Implement grading logic
    - A: 90-100
    - B: 80-89
    - C: 70-79
    - D: 60-69
    - F: 0-59
    """
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# TODO 2: Implement age validation for is_valid_age
def is_valid_age(age: int) -> bool:
    """
    Check if age is valid (between 0 and 120).

    Args:
        age: Age to validate

    Returns:
        True if valid, False otherwise

    TODO 2: Implement age validation
    """
    return 0 <= age <= 120


# TODO 3: Implement eligibility check for check_eligibility
def check_eligibility(age: int, has_license: bool, has_insurance: bool) -> bool:
    """
    Check if person is eligible to rent a car.

    Requirements:
    - Age must be >= 21
    - Must have driver's license
    - Must have insurance

    Args:
        age: Person's age
        has_license: Whether person has valid license
        has_insurance: Whether person has insurance

    Returns:
        True if eligible, False otherwise

    TODO 3: Implement eligibility check using logical operators (and/or)
    """
    return age >= 21 and has_license and has_insurance


# TODO 4: Implement temperature categorization
def categorize_temperature(temp_celsius: float) -> str:
    """
    Categorize temperature.

    Categories:
    - "freezing": < 0
    - "cold": 0-10
    - "cool": 11-20
    - "warm": 21-30
    - "hot": > 30

    Args:
        temp_celsius: Temperature in Celsius

    Returns:
        Temperature category

    TODO 4: Implement temperature categorization
    """
    if temp_celsius < 0:
        return "freezing"
    elif temp_celsius <= 10:
        return "cold"
    elif temp_celsius <= 20:
        return "cool"
    elif temp_celsius <= 30:
        return "warm"
    else:
        return "hot"


# Test cases
def test_control_flow():
    """Test all functions."""
    # Test check_grade
    assert check_grade(95) == "A", "95 should be A"
    assert check_grade(85) == "B", "85 should be B"
    assert check_grade(75) == "C", "75 should be C"
    assert check_grade(65) == "D", "65 should be D"
    assert check_grade(55) == "F", "55 should be F"

    # Test is_valid_age
    assert is_valid_age(25) == True, "25 is valid"
    assert is_valid_age(-5) == False, "-5 is invalid"
    assert is_valid_age(150) == False, "150 is invalid"

    # Test check_eligibility
    assert check_eligibility(25, True, True) == True, "Should be eligible"
    assert check_eligibility(18, True, True) == False, "Too young"
    assert check_eligibility(25, False, True) == False, "No license"

    # Test categorize_temperature
    assert categorize_temperature(-5) == "freezing"
    assert categorize_temperature(5) == "cold"
    assert categorize_temperature(15) == "cool"
    assert categorize_temperature(25) == "warm"
    assert categorize_temperature(35) == "hot"

    print("All tests passed!")


if __name__ == "__main__":
    test_control_flow()
