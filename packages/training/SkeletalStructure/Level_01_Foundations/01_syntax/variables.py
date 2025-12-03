"""
Skeletal Exercise: Python Variables
Level: 1 - Foundations
Topic: Syntax
Difficulty: 1/5
Duration: 10 minutes

Learning Objectives:
- Understand variable assignment in Python
- Learn naming conventions
- Practice different data types

Instructions:
Fill in the TODOs below to complete the variable exercises.
Do NOT look at the solution until you've attempted all TODOs.
"""

# TODO 1: Create a variable called 'name' and assign your name as a string
name = "AI Agent"

# TODO 2: Create a variable called 'age' and assign an integer value
age = 1

# TODO 3: Create a variable called 'is_learning' and assign a boolean value
is_learning = True

# TODO 4: Create a variable called 'score' and assign a float value
score = 95.5

# TODO 5: Print all four variables in a formatted string
# Expected output: "My name is [name], I am [age] years old, learning: [is_learning], score: [score]"
print(f"My name is {name}, I am {age} years old, learning: {is_learning}, score: {score}")

# ADVANCED TODO: Create multiple variables in a single line
# Hint: x, y, z = 1, 2, 3
x, y, z = 1, 2, 3


# Test your code
def test_variables():
    """
    Test function to verify your variables.

    This will check if all required variables are defined and have correct types.
    """
    # TODO 6: Implement test assertions
    # Hint: Use assert to check variable types
    # Example: assert isinstance(name, str), "name should be a string"
    assert isinstance(name, str), "name should be a string"
    assert isinstance(age, int), "age should be an integer"
    assert isinstance(is_learning, bool), "is_learning should be a boolean"
    assert isinstance(score, float), "score should be a float"
    assert isinstance(x, int) and isinstance(y, int) and isinstance(z, int), "x, y, z should be integers"


# Run tests
if __name__ == "__main__":
    test_variables()
    print("All tests passed!")
