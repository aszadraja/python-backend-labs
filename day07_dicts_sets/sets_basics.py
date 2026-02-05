"""
File: sets_basics.py
Day: 07
Topic: Sets - Basics
Author: Aszad Raja
Description:
    Practicing set creation and uniqueness property.
"""

# Status: Day 07 in progress

numbers = {1, 2, 3, 4, 4, 5, 5}

print(numbers)

numbers.add(6)
numbers.remove(3)

for num in numbers:
    print(num)

if __name__ == "__main__":
    print("Set basics executed successfully.")
