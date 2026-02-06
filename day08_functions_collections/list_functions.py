"""
File: list_functions.py
Day: 08
Topic: Functions with Lists
Author: Aszad Raja
Description:
    Using functions to process lists.
"""

# Status: Day 08 in progress

def find_max(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def count_even(numbers):
    count = 0
    for num in numbers:
        if num % 2 == 0:
            count += 1
    return count

nums = [3, 7, 2, 9, 4]

print("Max:", find_max(nums))
print("Even count:", count_even(nums))

if __name__ == "__main__":
    print("List functions executed successfully.")
