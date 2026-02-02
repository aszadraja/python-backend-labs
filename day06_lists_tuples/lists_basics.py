"""
File: lists_basics.py
Day: 06
Topic: Lists - Basics
Author: Aszad Raja
Description:
    Practicing list creation, indexing, and iteration.
"""

# Status: Day 06 in progress

numbers = [10, 20, 30, 40, 50]

print("First element:", numbers[0])
print("Last element:", numbers[-1])

numbers.append(60)
numbers.remove(20)

for num in numbers:
    print(num)

if __name__ == "__main__":
    print("List basics executed successfully.")
