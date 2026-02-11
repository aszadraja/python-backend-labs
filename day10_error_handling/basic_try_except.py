"""
File: basic_try_except.py
Day: 10
Topic: Exception Handling
Author: Aszad Raja
Description:
    Handling runtime errors safely.
"""

# Status: Day 10 in progress

try:
    num = int(input("Enter a number: "))
    result = 10 / num
    print("Result:", result)

except ZeroDivisionError:
    print("Cannot divide by zero.")

except ValueError:
    print("Invalid input. Please enter a number.")

finally:
    print("Execution finished.")

if __name__ == "__main__":
    print("Basic exception handling executed successfully.")
